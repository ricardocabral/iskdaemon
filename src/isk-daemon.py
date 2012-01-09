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
import os
import atexit
 
# isk-daemon imports
from core import settings
from core.imgdbapi import *
from core.facades import *

from imgSeekLib import utils
from imgSeekLib import daemonize

# Globals
rootLog = logging.getLogger('iskdaemon')
ServiceFacadeInstance = None

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
      
    rootLog.info('+- Starting HTTP service endpoints...')

    basePort = settings.core.getint('daemon', 'basePort')

    # TwistedMatrix imports
    from twisted.web import server, static
    from twisted.spread import pb
    from twisted.internet import reactor
    from twisted.internet.error import CannotListenError

    # Serve UI
    import ui 
    _ROOT = os.path.join(os.path.dirname(ui.__file__),"admin-www")
    if not os.path.exists(_ROOT): # on Windows? Try serving from current file dir
        import sys
        pathname, scriptname = os.path.split(sys.argv[0])
        _ROOT = os.path.join(pathname,'ui'+ os.sep + "admin-www")
    rootLog.info('| serving web admin from ' + _ROOT)        
    root = static.File(_ROOT)
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
