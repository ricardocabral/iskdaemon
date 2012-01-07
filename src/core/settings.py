# Config
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

