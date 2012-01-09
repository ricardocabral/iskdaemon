# -*- coding: iso-8859-1 -*-
###############################################################################
# begin                : Sun Jan  8 21:24:38 BRST 2012
# copyright            : (C) 2012 by Ricardo Niederberger Cabral
# email                : ricardo dot cabral at imgseek dot net
#
###############################################################################
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
###############################################################################

import utils
from imgdbapi import *

from twisted.web import xmlrpc, resource 
from twisted.spread import pb

class XMLRPCIskResource(xmlrpc.XMLRPC):
    """Will be injected with XML-RPC remote facade methods later"""
    pass

SOAPIskResource = None
# check for SOAP support
has_soap = True
try:
    from twisted.web import soap
except:
    has_soap = False

if has_soap:
    class nSOAPIskResource(soap.SOAPPublisher):
        """Will be injected with SOAP remote facade methods later"""
        pass
    SOAPIskResource = nSOAPIskResource
        
class DataExportResource(resource.Resource):
    """Bulk data export remote facade"""    
    isLeaf = False
    
    def render_GET(self, request):
        if request.args['m'][0] == 'imgidlist':
            dbid = int(request.args['dbid'][0])
            return ','.join([str(x) for x in getDbImgIdList(dbid)])
            
        return "Invalid method. <a href='/'>Return to main page</a>."

class iskPBClient:
    """Remote isk-daemon cluster peers mgmt"""

    def __init__(self, settings, addr):
        
        self.settings = settings
        
        self.addr = addr
        host,port = addr.split(':')
        self.host = host
        self.port = int(port) + 100
        self.root = None # hasn't connected yet
        self.imgIds = {}
        self.failedAttempts = 0

        # try first connection
        self.doFirstHandshake()

    def doFirstHandshake(self):
        rootLog.info('Attempting to connect to isk-deamon instance server at %s:%s ...' % (self.host,self.port))
        
        reactor.connectTCP(self.host, self.port, pbFactory) #IGNORE:E1101
        d = pbFactory.getRootObject()
        d.addCallback(self.connectSuccess)
        d.addErrback(self.connectFailed)
        
    def connectSuccess(self, object):
        rootLog.info("Peer connected succesfully: %s" % self.addr)
        self.root = object
        # announce myself
        self.root.callRemote("remoteConnected", 
                          self.settings.core.get('cluster', 'bindHostname')+":%d"%(self.settings.core.getint('daemon','basePort')))

    def connectFailed(self, reason):
        self.failedAttempts += 1
        rootLog.warn(reason)
        
    def resetFailures(self):
        self.failedAttempts = 0
        
    def onNewStatus(self, status):
        self.globalServerStats = status[1]
        self.imgIds = status[2]
        
    @utils.dumpArgs
    def hasImgId(self, dbId, imgId):
        for dbId in self.imgIds:
            if imgId in self.imgIds[dbId]: return True
        return False
    
class ServiceFacade(pb.Root):
    """Remote methods for isk-daemon server cluster comm"""
        
    peerRefreshRate = 2 # seconds between peer poll for status TODO: should be at settings.py
    maxFailedAttempts = 10
    
    def __init__(self, settings):
        self.settings = settings
        self.knownPeers = []
        self.peerAddressMap = {}
        self.externalFullAddr = self.settings.core.get('cluster', 'bindHostname')+":%d"%(self.settings.core.getint('daemon','basePort'))

        if self.settings.core.getboolean('cluster','isClustered'):
            global pbFactory
            pbFactory = pb.PBClientFactory()
            self.knownPeers = self.settings.core.get('cluster', 'seedPeers') #TODO parse/split list
            reactor.callLater(ServiceFacade.peerRefreshRate, self.refreshPeers) 
            rootLog.info('| Running in cluster mode')            
        else:
            pass
            #rootLog.info('| Cluster mode disabled')  #TODO uncomment when clustering works

    def peerFailed(self, reason, iskClient):
        rootLog.warn("Peer failed: "+iskClient.addr+" : "+str(reason))
        iskClient.failedAttempts += 1
        self.expirePeer(iskClient)
        
    def expirePeer(self, iskClient):
        if iskClient.failedAttempts > ServiceFacade.maxFailedAttempts:
            rootLog.warn("Instance at %s exceeded max failures. Removing from known peers." % iskClient.addr)
            del self.peerAddressMap[iskClient.addr]
            self.knownPeers.remove(iskClient.addr)

    def refreshPeers(self):
        
        def gotStatus(status,iskClient):            
            iskClient.resetFailures()
            #rootLog.debug("%s retd %s" %(iskClient.addr,status[0]))
            
            # sync db ids
            for dbid in status[2]:
                if not imgDB.isValidDB(dbid):
                    imgDB.createdb(dbid)
            
            # update stubs with new data
            iskClient.onNewStatus(status)
            
            # see if theres a new peer
            for addr in status[0]:
                self.remote_addPeer(addr)
                
        for peer in self.knownPeers:
            if peer == ():
                rootLog.error("instance shouldnt have itself as peer, removing")
                self.knownPeers.remove(peer)
                continue
            if not self.peerAddressMap.has_key(peer):
                self.remote_addPeer(peer)
                continue
            iskClient = self.peerAddressMap[peer]
            if not iskClient.root: # hasn't managed to connect and get proxy root obj yet
                iskClient.doFirstHandshake()
                self.expirePeer(iskClient)
                continue
            try:
                d = iskClient.root.callRemote("getStatus")
            except Exception, e:
                self.peerFailed(e,iskClient)
                continue
            d.addCallback(gotStatus, iskClient)
            d.addErrback(self.peerFailed, iskClient)

        # schedule next refresh
        reactor.callLater(ServiceFacade.peerRefreshRate, self.refreshPeers) #IGNORE:E1101        

    def remote_getStatus(self):
        #TODO implment using bloom filters
        #TODO cache for some seconds
        imgIds = {}
        for dbid in imgDB.getDBList():
            imgIds[dbid] = imgDB.getImgIdList(dbid) 
                            
        return [self.knownPeers+[self.externalFullAddr],
                getGlobalServerStats(),
                imgIds]

    def remote_addPeer(self, addr):
        # dont try to connect to myself
        if addr == (self.externalFullAddr): return False
        # add only if new
        if addr not in self.knownPeers:
            self.knownPeers.append(addr)
        if not self.peerAddressMap.has_key(addr):
            self.peerAddressMap[addr] = iskPBClient(self.settings, addr)
        return True

    def remote_remoteConnected(self, hostNamePort):
        rootLog.info('peer %s connected to me' % hostNamePort)        
        return self.remote_addPeer(hostNamePort)

def injectCommonDatabaseFacade(instance, prefix):
    for fcn in CommonDatabaseFacadeFunctions:
        setattr(instance, prefix+fcn.__name__, fcn)


