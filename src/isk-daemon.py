#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

###############################################################################
# begin                : Feb  5, 2007  4:58 PM
# copyright            : (C) 2003 by Ricardo Niederberger Cabral
# email                : ricardo dot cabral at imgseek dot net
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
###############################################################################

# General imports
import logging
import time
import os
import md5
import atexit
 
# isk-daemon imports
from core import settings
from imgSeekLib.ImageDB import ImgDB
from imgSeekLib import statistics
from imgSeekLib import utils
from imgSeekLib import daemonize
from imgSeekLib.urldownloader import urlToFile

# TwistedMatrix imports
from twisted.web import xmlrpc, resource, server, static
has_soap = True
try:
    from twisted.web import soap
except:
    has_soap = False
from twisted.spread import pb
from twisted.internet import reactor
from twisted.internet.error import *

# Globals
imgDB = None         # imgdb C lib singleton
pbFactory = None     # perspective factory
rootLog = logging.getLogger('isk-daemon')
ServiceFacadeInstance = None
remoteCache = None    # global remote cache (memcached) singleton
daemonStartTime = time.time()
hasShutdown = False

# Constants
iskVersion = "0.9"

############ Common functions for all comm backends
#@memoize.simple_memoized
def queryImgID(dbId, id, numres=12, fast=False):
    """
    Return the most similar images to the supplied one.

    @type  dbId: number
    @param dbId: Database space id.
    @type  id: number
    @param id: Target image id.
    @type  numres: number
    @param numres: Number of results to return. The target image is on the result list.
    @rtype:   array
    @return:  array of arrays: M{[[image id 1, score],[image id 2, score],[image id 3, score], ...]}
    """    
    dbId = int(dbId)
    id = int(id)
    numres = int(numres)
    
    # load balancing
    global ServiceFacadeInstance
    if settings.core.getboolean('cluster','isClustered') and not imgDB.isImageOnDB(dbId, id):
        for iskc in ServiceFacadeInstance.peerAddressMap.values():
            if iskc.hasImgId(dbId, id): # remote instance has this image. Forward query
                try:
                    d = iskc.root.callRemote("queryImgID", dbId,id,numres,fast)
                    return d #TODO this was using blockOn(d)
                except Exception, e:
                    #TODO peer failure should be noticed
                    #self.peerFailed(e,iskClient)
                    rootLog.error(e)
                    break
    # no remote peer has this image, try locally
    return imgDB.queryImgID(dbId, id, numres)

def addImg(dbId, id, filename, fileIsUrl=False):
    """
    Add image to database space. Image file is read, processed and indexed. After this indexing is done, image can be removed from file system.

    @type  dbId: number
    @param dbId: Database space id.
    @type  id: number
    @param id: Target image id. The image located on filename will be indexed and from now on should be refered to isk-daemon as this supplied id.
    @type  filename: string
    @param filename: Physical full file path for the image to be indexed. Should be in one of the supported formats ('jpeg', 'jpg', 'gif', 'png', 'rgb', 'pbm', 'pgm', 'ppm', 'tiff', 'tif', 'rast', 'xbm', 'bmp'). For better results image should have dimension of at least 128x128. Thumbnails are ok. Bigger images will be scaled down to 128x128.
    @type  fileIsUrl: boolean
    @param fileIsUrl: if true, filename is interpreted as an HTTP url and the remote image it points to downloaded and saved to a temporary location (same directory where database file is) before being added to database.
    @rtype:   number
    @return:  1 in case of success.
    """
    dbId = int(dbId)
    id = int(id)

    if fileIsUrl: # download it first
        tempFName = os.path.expanduser(settings.core.get('database','databasePath')) + ('_tmp_%d_%d.jpg' % (dbId,id))
        urlToFile(filename,tempFName)
        filename = tempFName
    res = 0
    try:
        #TODO id should be unsigned long int or something even bigger, also must review swig declarations
        res = imgDB.addImage(dbId, filename, id)
    except Exception, e:
        if str(e) == 'image already in db':
            rootLog.warn(e)        
        else:
            rootLog.error(e)
        return res
    
    if (fileIsUrl): os.remove(filename)    
    
    return res

def saveDb(dbId):
    """
    Save the supplied database space if the it has already been saved with a filename (previous call to L{saveDbAs}).
    B{NOTE}: This operation should be used for exporting single database spaces. For regular server instance database persistance, use L{saveAllDbs} and L{loadAllDbs}.

    @type  dbId: number
    @param dbId: Database space id.
    @rtype:   number
    @return:  1 in case of success.
    """        
    dbId = int(dbId)
    return imgDB.savedb(dbId)

def saveDbAs(dbId, filename):
    """
    Save the supplied database space if the it has already been saved with a filename (subsequent save calls can be made to L{saveDb}).

    @type  dbId: number
    @param dbId: Database space id.
    @type  filename: string
    @param filename: Target filesystem full path of the file where data should be stored at. B{NOTE}: This data file contains a single database space and should be used for import/export purposes only. Do not try to load it with a call to L{loadAllDbs}.
    @rtype:   number
    @return:  1 in case of success.
    """
    dbId = int(dbId)
    return imgDB.savedbas(dbId, filename)

def loadDb(dbId, filename):
    """
    Load the supplied single-database-space-dump into a database space of given id. An existing database space with the given id will be completely replaced.

    @type  dbId: number
    @param dbId: Database space id.
    @type  filename: string
    @param filename: Target filesystem full path of the file where data is stored at. B{NOTE}: This data file contains a single database space and should be used for import/export purposes only. Do not try to load it with a call to L{loadAllDbs} and vice versa.
    @rtype:   number
    @return:  dbId in case of success.
    """    
    dbId = int(dbId)    
    return imgDB.loaddb(dbId, filename)

def removeImg(dbId, id):
    """
    Remove image from database space.

    @type  dbId: number
    @param dbId: Database space id.
    @type  id: number
    @param id: Target image id.
    @rtype:   number
    @return:  1 in case of success.
    """    
    id = int(id)
    dbId = int(dbId)    
    return imgDB.removeImg(dbId, id)

def resetDb(dbId):
    """
    Removes all images from a database space, frees memory, reset statistics.

    @type  dbId: number
    @param dbId: Database space id.
    @rtype:   number
    @return:  1 in case of success.
    """    
    dbId = int(dbId)    
    return imgDB.resetdb(dbId)

def createDb(dbId):
    """
    Create new db space. Overwrite database space statistics if one with supplied id already exists.

    @type  dbId: number
    @param dbId: Database space id.
    @rtype:   number
    @return:  dbId in case of success
    """    
    dbId = int(dbId)
    return imgDB.createdb(dbId)
    
def shutdownServer():
    """
    Request a shutdown of this server instance.

    @rtype:   number
    @return:  always M{1}
    """
    global hasShutdown
    if hasShutdown: return 1 # already went through a shutdown
    
    if settings.core.getboolean('daemon','saveAllOnShutdown'):
            saveAllDbs()
            imgDB.closedb()

    rootLog.info("Shuting instance down...")
    reactor.callLater(1, reactor.stop) 
    hasShutdown = True
    return 1

def getDbImgCount(dbId):
    """
    Return count of indexed images on database space.

    @type  dbId: number
    @param dbId: Database space id.
    @rtype:   number
    @return:  image count
    """    
    dbId = int(dbId)
    return imgDB.getImgCount(dbId)

def isImgOnDb(dbId, id):
    """
    Return whether image id exists on database space.

    @type  dbId: number
    @param dbId: Database space id.
    @type  id: number
    @param id: Target image id.
    @rtype:   boolean
    @return:  true if image id exists
    """    
    dbId = int(dbId)
    id = int(id)
    return imgDB.isImageOnDB( dbId, id)

def getImgDimensions(dbId, id):
    """
    Returns image original dimensions when indexed into database.

    @type  dbId: number
    @param dbId: Database space id.
    @type  id: number
    @param id: Target image id.
    @rtype:   array
    @return:  array in the form M{[width, height]}
    """    
    dbId = int(dbId)
    id = int(id)
    return imgDB.getImageDimensions(dbId, id)

def calcImgAvglDiff(dbId, id1, id2):
    """
    Return average luminance (over three color channels) difference ratio

    @type  dbId: number
    @param dbId: Database space id.
    @type  id1: number
    @param id1: Target image 1 id.
    @type  id2: number
    @param id2: Target image 2 id.
    @rtype:   number
    @return:  float representing difference. The smaller, the most similar.
    """    
    dbId = int(dbId)
    id1 = int(id1)
    id2 = int(id2)
    return imgDB.calcAvglDiff(dbId, id1, id2)

def calcImgDiff(dbId, id1,  id2):
    """
    Return image similarity difference ratio

    @type  dbId: number
    @param dbId: Database space id.
    @type  id1: number
    @param id1: Target image 1 id.
    @type  id2: number
    @param id2: Target image 2 id.
    @rtype:   number
    @return:  float representing difference. The smaller, the most similar.
    """    
    dbId = int(dbId)
    id1 = int(id1)
    id2 = int(id2)
    
    return imgDB.calcDiff(dbId, id1,  id2)

def getImgAvgl(dbId, id1):
    """
    Return image average color levels on the three color channels (YIQ color system)

    @type  dbId: number
    @param dbId: Database space id.
    @type  id: number
    @param id: Target image id.
    @type  numres: number
    @param numres: The y intercept of the line.
    @rtype:   array
    @return:  array of arrays: M{[[image id 1, score],[image id 2, score],[image id 3, score], ...]}
    """    
    dbId = int(dbId)
    id1 = int(id1)
    return imgDB.getImageAvgl(dbId, id1)

def getDbIdsBloomFilter(dbId):
    """
    Returns a byte array (bloom filter) representing image ids on this server instance.
    
    B{Not yet implemented}    

    @type  dbId: number
    @param dbId: Database space id.
    @type  id: number
    @param id: Target image id.
    @type  numres: number
    @param numres: The y intercept of the line.
    @rtype:   array
    @return:  array of arrays: M{[[image id 1, score],[image id 2, score],[image id 3, score], ...]}
    """    
    dbId = int(dbId)
    return imgDB.getIdsBloomFilter(dbId)

def getDbList():
    """
    Return list defined database spaces.

    @rtype:   array
    @return:  array of db space ids
    """    
    return imgDB.getDBList()

def getDbImgIdList(dbId):
    """
    Return list of image ids on database space.

    @type  dbId: number
    @param dbId: Database space id.
    @rtype:   array
    @return:  array of image ids
    """    
    
    dbId = int(dbId)
    return imgDB.getImgIdList(dbId)

def getDbDetailedList():
    """
    Return details for all database spaces.

    @rtype:   map
    @return:  map key is database space id (as an integer), associated value is array with [getImgCount,
                            queryCount,
                            lastQueryPerMin,
                            queryMinCount,
                            queryMinCur,
                            lastAddPerMin,
                            addMinCount,
                            addMinCur,
                            addCount,
                            addSinceLastSave,
                            lastId,
                            lastSaveTime,
                            fileName
                            ]
    """    
    
    return imgDB.getDBDetailedList()

def saveAllDbsAs(path):
    """
    Persist all existing database spaces.

    @type  path: string
    @param path: Target filesystem full path of the file where data is stored at.
    @rtype:   number
    @return:  total db spaces written
    """    
    
    return imgDB.savealldbs(path)


def addKeywordImg(dbId, imgId, hash):
    """
    Adds a keyword to an image.

    @type  dbId: number
    @param dbId: Database space id.
    @type  imgId: number
    @param imgId: Target image id.
    @type  hash: number
    @param hash: Keyword id.
    @rtype:   boolean
    @return:  true if operation was succesful
    """
    dbId = int(dbId)
    imgId = int(imgId)
    return imgDB.addKeywordImg(dbId, imgId, hash)

def getIdsBloomFilter(dbId):
    """
    Return bloom filter containing all images on given db id.

    @type  dbId: number
    @param dbId: Database space id.
    @rtype:   bloom filter
    @return:  bloom filter containing all images on given db id.
    """
    dbId = int(dbId)
    return imgDB.getIdsBloomFilter(dbId)

def getClusterKeywords(dbId, numClusters,keywords):
    """
    Return whether image id exists on database space.

    @type  dbId: number
    @param dbId: Database space id.
    @type  id: number
    @param id: Target image id.
    @rtype:   boolean
    @return:  true if image id exists
    """    
    dbId = int(dbId)
    return imgDB.getClusterKeywords(dbId, numClusters,keywords)

def getClusterDb(dbId, numClusters):
    """
    Return whether image id exists on database space.

    @type  dbId: number
    @param dbId: Database space id.
    @type  id: number
    @param id: Target image id.
    @rtype:   boolean
    @return:  true if image id exists
    """    
    dbId = int(dbId)
    return imgDB.getClusterDb(dbId, numClusters)

def getKeywordsPopular(dbId, numres):
    """
    Return whether image id exists on database space.

    @type  dbId: number
    @param dbId: Database space id.
    @type  id: number
    @param id: Target image id.
    @rtype:   boolean
    @return:  true if image id exists
    """    
    dbId = int(dbId)
    return imgDB.getKeywordsPopular(dbId, numres)

def getKeywordsVisualDistance(dbId, distanceType,  keywords):
    """
    Return whether image id exists on database space.

    @type  dbId: number
    @param dbId: Database space id.
    @type  id: number
    @param id: Target image id.
    @rtype:   boolean
    @return:  true if image id exists
    """    
    dbId = int(dbId)
    return imgDB.getKeywordsVisualDistance(dbId, distanceType,  keywords)

def getAllImgsByKeywords(dbId, numres, kwJoinType, keywords):
    """
    Return all images with the given keywords

    @type  dbId: number
    @param dbId: Database space id.
    @type  kwJoinType: number
    @param kwJoinType Logical operator for target keywords: 1 for AND, 0 for OR
    @type  keywords: string
    @param keywords comma separated list of keyword ids. An empty string will return random images.
    @rtype:   array
    @return:  array of image ids
    """    
    dbId = int(dbId)
    keywordIds = [int(x) for x in keywords.split(',') if len(x) > 0]
    if len(keywordIds) == 0:
        keywordIds=[0]
    
    return imgDB.getAllImgsByKeywords(dbId, numres, kwJoinType, keywordIds)

def queryImgIDFastKeywords(dbId, imgId, numres, kwJoinType, keywords):
    """
    Fast query (only considers average color) for similar images considering keywords

    @type  dbId: number
    @param dbId: Database space id.
    @type  imgId: number
    @param imgId Target image id.
    @type  numres: number
    @param numres Number of results desired
    @type  kwJoinType: number
    @param kwJoinType logical operator for keywords: 1 for AND, 0 for OR
    @type  keywords: string
    @param keywords comma separated list of keyword ids. An empty string will return random images.
    @rtype:   array
    @return:  array of arrays: M{[[image id 1, score],[image id 2, score],[image id 3, score], ...]}
    """    
    dbId = int(dbId)
    imgId = int(imgId)
    keywordIds = [int(x) for x in keywords.split(',') if len(x) > 0]
    if len(keywordIds) == 0:
        keywordIds=[0]
    return imgDB.queryImgIDFastKeywords(dbId, imgId, numres, kwJoinType, keywords)

def queryImgIDKeywords(dbId, imgId, numres, kwJoinType, keywords):
    """
    Query for similar images considering keywords. The input keywords are used for narrowing the
    search space.

    @type  dbId: number
    @param dbId: Database space id.
    @type  imgId: number
    @param imgId Target image id.
    @type  numres: number
    @param numres Number of results desired
    @type  kwJoinType: number
    @param kwJoinType logical operator for keywords: 1 for AND, 0 for OR
    @type  keywords: string
    @param keywords comma separated list of keyword ids. An empty string will return random images.
    @rtype:   array
    @return:  array of arrays: M{[[image id 1, score],[image id 2, score],[image id 3, score], ...]}
    """    
    dbId = int(dbId)
    imgId = int(imgId)
    keywordIds = [int(x) for x in keywords.split(',') if len(x) > 0]
    if len(keywordIds) == 0:
        keywordIds=[0]
    return imgDB.queryImgIDKeywords(dbId, imgId, numres, kwJoinType, keywordIds)

def mostPopularKeywords(dbId, imgs, excludedKwds, count, mode):
    """
    Returns the most frequent keywords associated with a given set of images 

    @type  dbId: number
    @param dbId Database space id.
    @type  imgs: string
    @param imgs Comma separated list of target image ids
    @type  excludedKwds: string
    @param excludedKwds Comma separated list of keywords ids to be excluded from the frequency count
    @type  count: number
    @param count Number of keyword results desired
    @type  mode: number
    @param mode ignored, will be used on future versions.
    @rtype:   array
    @return:  array of keyword ids and frequencies: [kwd1_id, kwd1_freq, kwd2_id, kwd2_freq, ...]
    """    
    dbId = int(dbId)
    excludedKwds = [int(x) for x in excludedKwds.split(',') if len(x) > 0]
    imgs = [int(x) for x in imgs.split(',') if len(x) > 0]
    
    return imgDB.mostPopularKeywords(dbId, imgs, excludedKwds, count, mode)

def getKeywordsImg(dbId, imgId):
    """
    Returns all keywords currently associated with an image.

    @type  dbId: number
    @param dbId: Database space id.
    @type  imgId: number
    @param imgId: Target image id.
    @rtype:   array
    @return:  array of keyword ids
    """    
    dbId = int(dbId)
    imgId = int(imgId)
    return imgDB.getKeywordsImg(dbId, imgId)

def removeAllKeywordImg(dbId, imgId):
    """
    Remove all keyword associations this image has.
    
    Known issue: keyword based queries will continue to consider the image to be associated to this keyword until the database is saved and restored.

    @type  dbId: number
    @param dbId: Database space id.
    @type  imgId: number
    @param imgId: Target image id.
    @rtype:   boolean
    @return:  true if operation succeeded
    """    
    dbId = int(dbId)
    imgId = int(imgId)
    return imgDB.removeAllKeywordImg(dbId, imgId)

def removeKeywordImg(dbId, imgId, hash):
    """
    Remove the association of a keyword to an image
    
    Known issue: keyword based queries will continue to consider the image to be associated to this keyword until the database is saved and restored.    

    @type  dbId: number
    @param dbId: Database space id.
    @type  imgId: number
    @param imgId: Target image id.
    @type  hash: number
    @param hash: Keyword id.
    @rtype:   boolean
    @return:  true if operation succeeded
    """    
    dbId = int(dbId)
    imgId = int(imgId)
    return imgDB.removeKeywordImg(dbId, imgId, hash)

def addKeywordsImg(dbId, imgId, hashes):
    """
    Associate keywords to image

    @type  dbId: number
    @param dbId: Database space id.
    @type  imgId: number
    @param imgId: Target image id.
    @type  hashes: list of number
    @param hashes: Keyword hashes to associate
    @rtype:   boolean
    @return:  true if image id exists
    """    
    dbId = int(dbId)
    imgId = int(imgId)
    return imgDB.addKeywordsImg(dbId, imgId, hashes)

def addDir(dbId, path, recurse):
    """
    Visits a directory recursively and add supported images into database space.

    @type  dbId: number
    @param dbId: Database space id.
    @type  path: string
    @param path: Target filesystem full path of the initial dir.
    @type  recurse: number
    @param recurse: 1 if should visit recursively
    @rtype:   number
    @return:  count of images succesfully added
    """    
    
    dbId = int(dbId)
    return imgDB.addDir(dbId, path, recurse)

def loadAllDbsAs(path):
    """
    Loads from disk all previously persisted database spaces. (File resulting from a previous call to L{saveAllDbs}).

    @type  path: string
    @param path: Target filesystem full path of the file where data is stored at.
    @rtype:   number
    @return:  total db spaces read
    """    
    
    return imgDB.loadalldbs(path)

def saveAllDbs():
    """
    Persist all existing database spaces on the data file defined at the config file I{settings.py}

    @rtype:   number
    @return:  count of persisted db spaces
    """
    
    return imgDB.savealldbs(settings.core.get('database','databasePath'))

def loadAllDbs():
    """
    Loads from disk all previously persisted database spaces on the data file defined at the config file I{settings.py}

    @rtype:   number
    @return:  count of persisted db spaces
    """    
    
    return imgDB.loadalldbs(settings.core.get('database','databasePath'))

def removeDb(dbid):
    """
    Remove a database. All images associated with it are also removed.

    @rtype:   boolean
    @return:  true if succesful
    """    
    
    return imgDB.removeDb(dbid)

def getGlobalServerStats():
    """
    Return the most similar images to the supplied one.

    @rtype:   map
    @return:  key is stat name, value is value. Keys are ['isk-daemon uptime', 'Number of databases', 'Total memory usage', 'Resident memory usage', 'Stack memory usage']
    """    
    
    stats = {}
    
    stats['isk-daemon uptime'] = statistics.human_readable(time.time() - daemonStartTime)
    stats['Number of databases'] = len(imgDB.getDBList())
    stats['Total memory usage'] = statistics.memory()
    stats['Resident memory usage'] = statistics.resident()
    stats['Stack memory usage'] = statistics.stacksize()    
    
    return stats

def isValidDb(dbId):
    """
    Return whether database space id has already been defined

    @type  dbId: number
    @param dbId: Database space id.
    @rtype:   boolean
    @return:  True if exists
    """    
    
    dbId = int(dbId)
    return imgDB.isValidDB(dbId)

CommonDatabaseFacadeFunctions = [
                                 queryImgID,
                                 addImg,
                                 saveDb,
                                 loadDb,
                                 removeImg,
                                 resetDb,
                                 removeDb,
                                 createDb,
                                 getDbImgCount,
                                 isImgOnDb,
                                 getImgDimensions,
                                 calcImgAvglDiff,
                                 calcImgDiff,
                                 getImgAvgl,
                                 getDbIdsBloomFilter,
                                 getDbList,
                                 getDbDetailedList,
                                 getDbImgIdList,
                                 isValidDb,
                                 getGlobalServerStats,
                                 saveDbAs,
                                 saveAllDbs,
                                 loadAllDbs,
                                 saveAllDbsAs,
                                 loadAllDbsAs,
                                 addDir,
                                 shutdownServer,
                                 addKeywordImg,
                                 addKeywordsImg,
                                 removeKeywordImg,
                                 removeAllKeywordImg,
                                 getKeywordsImg,
                                 queryImgIDKeywords,
                                 queryImgIDFastKeywords,
                                 getAllImgsByKeywords,
                                 getKeywordsVisualDistance,
                                 getKeywordsPopular,
                                 getClusterDb,
                                 getClusterKeywords,
                                 getIdsBloomFilter,     
                                 mostPopularKeywords,                                                             
                                    ]

class XMLRPCIskResource(xmlrpc.XMLRPC):
    """Will be injected with XML-RPC remote facade methods later"""
    pass

SOAPIskResource = None

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

def startIskDaemon():    
    """ cmd-line daemon entry-point
    """

    # parse command line    
    from optparse import OptionParser
        
    parser = OptionParser(version="%prog "+iskVersion)
    #TODO-2 add option
    #parser.add_option("-f", "--file", dest="filename",
    #                  help="read settings from a file other than 'settings.py'", metavar="FILE")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print debug messages to stdout")
    (options, args) = parser.parse_args()
   
    #TODO-2 show which file was read
    #rootLog.info('+- Reading settings from "%s"' % options.filename)
    if settings.core.getboolean('daemon','startAsDaemon'): daemonize.createDaemon()
        
    global imgDB
      
    # misc daemon inits
    rootLog.info('+- Initializing image database (Version %s) ...' % iskVersion)
    imgDB = ImgDB(settings)
    imgDB.loadalldbs(os.path.expanduser(settings.core.get('database', 'databasePath')))
    
    rootLog.info('| image database initialized')
    rootLog.info('+- Starting HTTP service endpoints...')

    basePort = settings.core.getint('daemon', 'basePort')

    import ui 
    _ROOT = os.path.dirname(ui.__file__)
    root = static.File(os.path.join(_ROOT,"admin-www"))
    rootLog.info('| web admin interface listening for requests at http://localhost:%d/'% basePort)
    
    atexit.register(shutdownServer)
        
    # prepare remote command interfaces
    XMLRPCIskResourceInstance = XMLRPCIskResource()
    injectCommonDatabaseFacade(XMLRPCIskResourceInstance, 'xmlrpc_')

    if has_soap:
        SOAPIskResourceInstance = SOAPIskResource()
        injectCommonDatabaseFacade(SOAPIskResourceInstance, 'soap_')
    
        # expose remote command interfaces
        root.putChild('SOAP', SOAPIskResourceInstance)
        rootLog.info('| listening for SOAP requests at http://localhost:%d/SOAP'% basePort)
    else:
        rootLog.info('| Not listening for SOAP requests. Installing "SOAPpy" python package to enable it.')

    global ServiceFacadeInstance
    ServiceFacadeInstance = ServiceFacade(settings)
    injectCommonDatabaseFacade(ServiceFacadeInstance, 'remote_')

    # expose remote command interfaces
    root.putChild('RPC', XMLRPCIskResourceInstance)
    rootLog.info('| listening for XML-RPC requests at http://localhost:%d/RPC'% basePort)

    root.putChild('export', DataExportResource())
    rootLog.debug('| listening for data export requests at http://localhost:%d/export'% basePort)

    # start twisted reactor
    try:
        reactor.listenTCP(basePort, server.Site(root)) 
        rootLog.info('| HTTP service endpoints started. Binded to all local network interfaces.')
    except CannotListenError:
        rootLog.error("Socket port %s seems to be in use, is there another instance already running ? Try supplying a different one on the command line as the first argument. Cannot start isk-daemon." % basePort)
        return
        
    rootLog.debug('+- Starting internal service endpoint...')
    reactor.listenTCP(basePort+100, pb.PBServerFactory(ServiceFacadeInstance)) 
    rootLog.debug('| internal service listener started at pb://localhost:%d'% (basePort+100))
    rootLog.info('| Binded to all local network interfaces.')
    
    rootLog.info('+ init finished. Waiting for requests ...')
    reactor.run() 

if __name__ == "__main__":
    startIskDaemon()
    # profiling
    """
    import profile
    profile.run('startIskDaemon()', 'isk.prof')
    """
