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

__doc__ = '''
@undocumented:  getClusterKeywords getClusterDb getKeywordsPopular getKeywordsVisualDistance getIdsBloomFilter
 '''

import time
import logging
import os

import statistics
from urldownloader import urlToFile
import settings
from imgSeekLib.ImageDB import ImgDB

# Globals
remoteCache = None    # global remote cache (memcached) singleton
pbFactory = None     # perspective factory
daemonStartTime = time.time()
hasShutdown = False
iskVersion = "0.9.2"

# misc daemon inits
rootLog = logging.getLogger('imgdbapi')
rootLog.info('+- Initializing isk-daemon server (version %s) ...' % iskVersion)
imgDB = ImgDB(settings)
imgDB.loadalldbs(os.path.expanduser(settings.core.get('database', 'databasePath')))

rootLog.info('| image database initialized')


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
    from twisted.internet import reactor
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

def getImgAvgl(dbId, id):
    """
    Return image average color levels on the three color channels (YIQ color system)

    @type  dbId: number
    @param dbId: Database space id.
    @type  id: number
    @param id: Target image id.
    @rtype:   array of double
    @return:  values for YIQ color channels
    """    
    dbId = int(dbId)
    id1 = int(id1)
    return imgDB.getImageAvgl(dbId, id1)

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
    @param kwJoinType: Logical operator for target keywords: 1 for AND, 0 for OR
    @type  keywords: string
    @param keywords: comma separated list of keyword ids. An empty string will return random images.
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
    @param imgId Target image id. If '0', random images containing the target keywords will be returned.
    @type  numres: number
    @param numres Number of results desired
    @type  kwJoinType: number
    @param kwJoinType: logical operator for keywords: 1 for AND, 0 for OR
    @type  keywords: string
    @param keywords: comma separated list of keyword ids.
    @rtype:   array
    @return:  array of arrays: M{[[image id 1, score],[image id 2, score],[image id 3, score], ...]}
    """    
    dbId = int(dbId)
    imgId = int(imgId)
    keywordIds = [int(x) for x in keywords.split(',') if len(x) > 0]
    return imgDB.queryImgIDFastKeywords(dbId, imgId, numres, kwJoinType, keywords)

def queryImgIDKeywords(dbId, imgId, numres, kwJoinType, keywords):
    """
    Query for similar images considering keywords. The input keywords are used for narrowing the
    search space.

    @type  dbId: number
    @param dbId: Database space id.
    @type  imgId: number
    @param imgId: Target image id. If '0', random images containing the target keywords will be returned.
    @type  numres: number
    @param numres: Number of results desired
    @type  kwJoinType: number
    @param kwJoinType: logical operator for keywords: 1 for AND, 0 for OR
    @type  keywords: string
    @param keywords: comma separated list of keyword ids. 
    @rtype:   array
    @return:  array of arrays: M{[[image id 1, score],[image id 2, score],[image id 3, score], ...]}
    """    
    dbId = int(dbId)
    imgId = int(imgId)
    keywordIds = [int(x) for x in keywords.split(',') if len(x) > 0]
    return imgDB.queryImgIDKeywords(dbId, imgId, numres, kwJoinType, keywordIds)

def mostPopularKeywords(dbId, imgs, excludedKwds, count, mode):
    """
    Returns the most frequent keywords associated with a given set of images 

    @type  dbId: number
    @param dbId Database space id.
    @type  imgs: string
    @param imgs: Comma separated list of target image ids
    @type  excludedKwds: string
    @param excludedKwds: Comma separated list of keywords ids to be excluded from the frequency count
    @type  count: number
    @param count Number of keyword results desired
    @type  mode: number
    @param mode: ignored, will be used on future versions.
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


