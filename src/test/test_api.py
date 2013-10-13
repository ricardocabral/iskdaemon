#!/usr/bin/env python
# -*- coding: UTF-8 -*-

###############################################################################
# begin                : Sun Jan  8 23:42:48 BRST 2012
# copyright            : Ricardo Niederberger Cabral
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
#
###############################################################################

import xmlrpclib

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-d", "--datadir", 
                  dest="datadir",
                  help="local data dir",
                  default='/Users/rnc/Projects/iskdaemon/src/test/data/'
                    )
parser.add_option("-s", "--server",
                  dest="server", 
                  help="server rpc endpoint url",
                  default='http://127.0.0.1:31128/RPC'
                    )

(options, args) = parser.parse_args()

server_url = options.server
data_dir = options.datadir    

def start_test(x): print x

def testAddImage():
    print server_url
    print data_dir
    server = xmlrpclib.ServerProxy(server_url);

    assert server.createDb(1) == True
    
    start_test('add imgs')
    
    assert server.addImg(1, 7,data_dir+"DSC00007.JPG") == 1
    assert server.addImg(1, 6,data_dir+"DSC00006.JPG") == 1
    assert server.addImg(1, 14,data_dir+"DSC00014.JPG") == 1
    assert server.addImg(1, 17,data_dir+"DSC00017.JPG") == 1
    
    start_test('img count')
    
    assert server.getDbImgCount(1) == 4
    
    start_test('image is on db')
    
    assert server.isImgOnDb(1,7) == True
    
    start_test('save db')
    
    assert server.saveAllDbs() > 1
    
    start_test('reset db')
    
    assert server.resetDb(1) == 1
    assert server.getDbImgCount(1) == 0
    
    start_test('load db')
    
    assert server.loadAllDbs() > 0
    
    assert server.getDbImgCount(1) == 4
    
    assert server.isImgOnDb(1,7) == 1
    assert server.isImgOnDb(1,733) == 0
    
    start_test('remove img')
    
    assert server.removeImg(1,7) == 1
    assert server.removeImg(1,73232) == 0
    assert server.getDbImgCount(1) == 3
    assert server.isImgOnDb(1,7) == 0
    assert server.getDbImgIdList(1) == [6,14,17]
            
    start_test('list database spaces')
    
    assert 1 in server.getDbList() 
    
    start_test('add more random images')
    
    fnames = [data_dir+"DSC00007.JPG",
              data_dir+"DSC00006.JPG",
              data_dir+"DSC00014.JPG",
              data_dir+"DSC00017.JPG"
              ]
    
    import random
    for i in range(20,60):
        assert server.addImg(1, i, random.choice(fnames)) == 1
    
    start_test('add keywords')
    
    assert server.addKeywordImg(1,142,3) == False
    assert server.addKeywordImg(1,14,1) == True
    assert server.addKeywordImg(1,14,2) == True
    assert server.addKeywordImg(1,14,3) == True
    assert server.addKeywordImg(1,14,4) == True
    assert server.addKeywordImg(1,17,3) == True
    assert server.addKeywordImg(1,21,3) == True
    assert server.addKeywordImg(1,22,5) == True
    
    start_test('get keywords')
    
    assert server.getKeywordsImg(1,14) == [1,2,3,4]
    assert server.getKeywordsImg(1,17) == [3]
    assert server.getKeywordsImg(1,21) == [3]
    assert server.getKeywordsImg(1,20) == []
    
    start_test('remove keywords')
    
    assert server.removeAllKeywordImg(1,17) == True
    assert server.getKeywordsImg(1,17) == []
    
    start_test('save db')
    
    assert server.saveAllDbs() > 1
    
    start_test('reset db')
    
    assert server.resetDb(1) == 1
    assert server.getDbImgCount(1) == 0
    
    start_test('load db')
    
    assert server.loadAllDbs() > 1
    assert server.getDbImgCount(1) == 43
    
    start_test('get keywords')
    
    assert server.getKeywordsImg(1,14) == [1,2,3,4]

    start_test('query by a keyword')

    # 3: 14, 17, 21
    # 4: 14
    # 5: 22
    
    
    res = server.getAllImgsByKeywords(1, 30, 1, '3')
    assert 14 in res
    assert 17 in res
    assert 21 in res 

    res = server.getAllImgsByKeywords(1, 30, 0, '3,4')
    assert 14 in res
    assert 17 in res
    assert 21 in res
     
    res = server.getAllImgsByKeywords(1, 30, 0, '3,4,5')
    assert 14 in res
    assert 17 in res
    assert 21 in res 
    assert 22 in res 

    res = server.getAllImgsByKeywords(1, 30, 1, '5') 
    assert 22 in res
     
    res = server.getAllImgsByKeywords(1, 30, 1, '3,4') 
    assert 14 in res
    
    start_test('query similarity')
    
    assert len(server.queryImgID(1,6, 3)) == 4    

    start_test('query similarity by a keyword')
    
    #def queryImgIDKeywords(dbId, imgId, numres, kwJoinType, keywords):
    res = server.queryImgIDKeywords(1,6, 3,0,'3,4')
    resids = [r[0] for r in res]
    assert 17 in resids
   
   #  start_test('mostPopularKeywords')
   #  
   #  assert server.addKeywordImg(1,50,1) == True
   #  assert server.addKeywordImg(1,50,2) == True
   #  assert server.addKeywordImg(1,50,3) == True
   #  assert server.addKeywordImg(1,51,1) == True
   #  assert server.addKeywordImg(1,51,2) == True
   #  assert server.addKeywordImg(1,51,3) == True
   #  assert server.addKeywordImg(1,52,3) == True
   #  
   # # dbId, imgs, excludedKwds, count, mode    
   #  res = server.mostPopularKeywords(1, '50,51,52', '1', 3, 0)
   #  resmap = {}
   #  for i in range(len(res)/2):
   #      resmap[res[i*2]] = res[i*2+1]
   #  assert 1 not in resmap.keys()
   #  assert resmap[3] == 3
    

    #assertEqual(1,server.addImg(1,test_images_dir+"DSC00006.JPG",6,))

import unittest

class APITest(unittest.TestCase):
    
    def setUp(self):
        self.server = xmlrpclib.ServerProxy(server_url);

    def tearDown(self):
        pass

    def testGetLog(self):
        logs = self.server.getIskLog(2)
        print logs
        assert len(logs)> 10

    def testAddBlob(self):
        data = open(data_dir+"DSC00007.JPG",'rb').read()
        assert self.server.addImgBlob(1, 7,xmlrpclib.Binary(data)) 

    #TODO refactor the rest of tests into here

if __name__ == '__main__':
    testAddImage()
    unittest.main()
