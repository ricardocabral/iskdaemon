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

import ConfigParser
import os
import logging

logger = logging.getLogger('isk-daemon')

# Defaults
core = ConfigParser.SafeConfigParser({
    'startAsDaemon' : 'false',                     # run as background process on UNIX systems
    'basePort' : '31128',                          # base tcp port to start listening at for HTTP requests (admin interface, XML-RPC requests, etc)
    'debug' : 'true',                              # print debug messages to console
    'saveAllOnShutdown' : 'true',                  # automatically save all database spaces on server shutdown
    'databasePath' : "~/isk-db",                 # file where to store database files
    'saveInterval' : '120'    ,                    # seconds between each automatic database save
    'automaticSave' : 'false' ,                    # whether the database should be saved automatically
    'isClustered' : 'false'   ,                     # run in cluster mode ? If True, make sure subsequent settings are ok
    'seedPeers' : 'isk2host:31128',                            
    'bindHostname': 'isk1host' ,                 # hostname for this instance. Other instances may try to connect to this hostname
    'logPath': 'isk-daemon.log',
    'logDebug': 'true',
    })

# read from many possible locations
if not core.read(['isk-daemon.conf', 
            os.path.expanduser('~/.isk-daemon.conf'), 
            "/etc/iskdaemon/isk-daemon.conf", 
            #os.path.join(os.environ.get("ISKCONF"),'isk-daemon.conf'),
            ]):
    logger.error('no config file (isk-daemon.conf) found. Looked at local dir, home user dir and /etc/iskdaemon. Using defaults for everything.')

for sec in ['database', 'daemon','cluster']:
    if not core.has_section(sec): core.add_section(sec)

# perform some clean up/bulletproofing
core.set('database', 'databasePath', os.path.expanduser(core.get('database','databasePath')))

# fix windows stuff
if os.name == 'nt': # fix windows stuff
    core.set('database', 'databasePath', os.path.expanduser(core.get('database','databasePath').replace('/','\\')))

def setupLogging():
    # set up logging to file - see previous section for more details
    if core.getboolean('daemon','logDebug'): 
        llevel = logging.DEBUG
    else:
        llevel = logging.INFO
    logging.basicConfig(level = llevel,
                        format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt = '%m-%d %H:%M',
                        filename = core.get('daemon','logPath'),
                        )
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)  # INFO
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
    
setupLogging()

