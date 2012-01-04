# Config
import ConfigParser
import os

# Defaults
core = ConfigParser.SafeConfigParser({
    'startAsDaemon' : False,                     # run as background process on UNIX systems
    'basePort' : 31128,                          # base tcp port to start listening at for HTTP requests (admin interface, XML-RPC requests, etc)
    'debug' :True,                              # print debug messages to console
    'saveAllOnShutdown' : True,                  # automatically save all database spaces on server shutdown
    'databasePath' : "~/isk-db",                 # file where to store database files
    'saveInterval' : 120    ,                    # seconds between each automatic database save
    'automaticSave' : False ,                    # whether the database should be saved automatically
    'isClustered' : False   ,                     # run in cluster mode ? If True, make sure subsequent settings are ok
    'seedPeers' : 'isk2host:31128',                            
    'bindHostname': 'isk1host' ,                 # hostname for this instance. Other instances may try to connect to this hostname
    })

# read from many possible locations
core.read(['isk-daemon.conf', 
            os.path.expanduser('~/.isk-daemon.conf'), 
            "/etc/iskdaemon/isk-daemon.conf", 
            #os.path.join(os.environ.get("ISKCONF"),'isk-daemon.conf'),
            ])

# perform some clean up/bulletproofing
core.set('database', 'databasePath', os.path.expanduser(core.get('database','databasePath')))

# fix windows stuff
if os.name == 'nt': # fix windows stuff
    core.set('database', 'databasePath', os.path.expanduser(core.get('database','databasePath').replace('/','\\')))

