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

import unittest
import xmlrpclib

data_dir = '/Users/rnc/Projects/iskdaemon/src/test/data/'

def start_test(x): print x

class ImageDBTest(unittest.TestCase):
    
    def setUp(self):
        server_url = 'http://127.0.0.1:31128/RPC';
        self.server = xmlrpclib.ServerProxy(server_url);

    def tearDown(self):
        pass

    def testAddImage(self):
        assert self.server.createDb(1) == True
        
        start_test('add imgs')
        
        assert self.server.addImg(1, 7,data_dir+"DSC00007.JPG") == 1
        assert self.server.addImg(1, 6,data_dir+"DSC00006.JPG") == 1
        assert self.server.addImg(1, 14,data_dir+"DSC00014.JPG") == 1
        assert self.server.addImg(1, 17,data_dir+"DSC00017.JPG") == 1
        
        start_test('img count')
        
        assert self.server.getDbImgCount(1) == 4
        
        start_test('image is on db')
        
        assert self.server.isImgOnDb(1,7) == True
        
        start_test('save db')
        
        assert self.server.saveAllDbs() == 1
        
        start_test('reset db')
        
        assert self.server.resetDb(1) == 1
        assert self.server.getDbImgCount(1) == 0
        
        start_test('load db')
        
        assert self.server.loadAllDbs() == 1
        
        assert self.server.getDbImgCount(1) == 4
        
        assert self.server.isImgOnDb(1,7) == 1
        assert self.server.isImgOnDb(1,733) == 0
        
        start_test('remove img')
        
        assert self.server.removeImg(1,7) == 1
        assert self.server.removeImg(1,73232) == 0
        assert self.server.getDbImgCount(1) == 3
        assert self.server.isImgOnDb(1,7) == 0
        assert self.server.getDbImgIdList(1) == [6,14,17]
                
        start_test('list database spaces')
        
        assert self.server.getDbList() == [1]
        
        start_test('add more random images')
        
        fnames = [data_dir+"DSC00007.JPG",
                  data_dir+"DSC00006.JPG",
                  data_dir+"DSC00014.JPG",
                  data_dir+"DSC00017.JPG"
                  ]
        
        import random
        for i in range(20,60):
            assert self.server.addImg(1, i, random.choice(fnames)) == 1
        
        start_test('add keywords')
        
        assert self.server.addKeywordImg(1,142,3) == False
        assert self.server.addKeywordImg(1,14,1) == True
        assert self.server.addKeywordImg(1,14,2) == True
        assert self.server.addKeywordImg(1,14,3) == True
        assert self.server.addKeywordImg(1,14,4) == True
        assert self.server.addKeywordImg(1,17,3) == True
        assert self.server.addKeywordImg(1,21,3) == True
        assert self.server.addKeywordImg(1,22,5) == True
        
        start_test('get keywords')
        
        assert self.server.getKeywordsImg(1,14) == [1,2,3,4]
        assert self.server.getKeywordsImg(1,17) == [3]
        assert self.server.getKeywordsImg(1,21) == [3]
        assert self.server.getKeywordsImg(1,20) == []
        
        start_test('remove keywords')
        
        assert self.server.removeAllKeywordImg(1,17) == True
        assert self.server.getKeywordsImg(1,17) == []
        
        start_test('save db')
        
        assert self.server.saveAllDbs() == 1
        
        start_test('reset db')
        
        assert self.server.resetDb(1) == 1
        assert self.server.getDbImgCount(1) == 0
        
        start_test('load db')
        
        assert self.server.loadAllDbs() == 1
        assert self.server.getDbImgCount(1) == 43
        
        start_test('get keywords')
        
        assert self.server.getKeywordsImg(1,14) == [1,2,3,4]

        start_test('query by a keyword')

        # 3: 14, 17, 21
        # 4: 14
        # 5: 22
        
        
        res = self.server.getAllImgsByKeywords(1, 30, 1, '3')
        assert 14 in res
        assert 17 in res
        assert 21 in res 

        res = self.server.getAllImgsByKeywords(1, 30, 0, '3,4')
        assert 14 in res
        assert 17 in res
        assert 21 in res
         
        res = self.server.getAllImgsByKeywords(1, 30, 0, '3,4,5')
        assert 14 in res
        assert 17 in res
        assert 21 in res 
        assert 22 in res 

        res = self.server.getAllImgsByKeywords(1, 30, 1, '5') 
        assert 22 in res
         
        res = self.server.getAllImgsByKeywords(1, 30, 1, '3,4') 
        assert 14 in res
        
        start_test('query similarity')
        
        assert len(self.server.queryImgID(1,6, 3)) == 4    

        start_test('query similarity by a keyword')
        
        #def queryImgIDKeywords(dbId, imgId, numres, kwJoinType, keywords):
        res = self.server.queryImgIDKeywords(1,6, 3,0,'3,4')
        resids = [r[0] for r in res]
        assert 17 in resids
       
       #  start_test('mostPopularKeywords')
       #  
       #  assert self.server.addKeywordImg(1,50,1) == True
       #  assert self.server.addKeywordImg(1,50,2) == True
       #  assert self.server.addKeywordImg(1,50,3) == True
       #  assert self.server.addKeywordImg(1,51,1) == True
       #  assert self.server.addKeywordImg(1,51,2) == True
       #  assert self.server.addKeywordImg(1,51,3) == True
       #  assert self.server.addKeywordImg(1,52,3) == True
       #  
       # # dbId, imgs, excludedKwds, count, mode    
       #  res = self.server.mostPopularKeywords(1, '50,51,52', '1', 3, 0)
       #  resmap = {}
       #  for i in range(len(res)/2):
       #      resmap[res[i*2]] = res[i*2+1]
       #  assert 1 not in resmap.keys()
       #  assert resmap[3] == 3
        

        #self.assertEqual(1,self.server.addImg(1,test_images_dir+"DSC00006.JPG",6,))
     
if __name__ == '__main__':
    unittest.main() 
