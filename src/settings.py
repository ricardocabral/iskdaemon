################################################################################
# isk-daemon settings
# change the variables below to customize isk-daemon behavior
################################################################################

###### daemon settings
startAsDaemon = False                     # run as background process on UNIX systems
basePort = 31128                          # base tcp port to start listening at for HTTP requests (admin interface, XML-RPC requests, etc)
debug = True                              # print debug messages to console
saveAllOnShutdown = True                  # automatically save all database spaces on server shutdown

###### database settings
databasePath = "~/isk-db"                 # file where to store database files
saveInterval = 120                        # seconds between each automatic database save
automaticSave = False                     # whether the database should be saved automatically

###### cluster settings
isClustered = False                        # run in cluster mode ? If True, make sure subsequent settings are ok
# initial list of server instances on this cluster. List of strings with the format "hostname:service_port" (internal service endpoint)
seedPeers = ['isk2host:31128']                            
bindHostname = 'isk1host'                  # hostname for this instance. Other instances may try to connect to this hostname

