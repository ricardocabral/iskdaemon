#!/usr/bin/env python
# -*- coding: UTF-8 -*-

###############################################################################
# begin                : 2008-12-04
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
from imgSeekLib.ImageDB import ImgDB 
from core import settings

test_images_dir = 'test/data/'

class ImageDBTest(unittest.TestCase):
    
    def setUp(self):
        self.imgdb = ImgDB(settings)
        self.assertEqual(1,self.imgdb.createdb(1))

    def tearDown(self):
        #self.assertEqual(1,self.imgdb.resetdb(1));
        #self.imgdb.closedb()  
        pass

    def testAddImageUTF8(self):
        self.assertEqual(1,self.imgdb.addImage(1,test_images_dir+"テスト.JPG",6,))
        self.assertEqual(1,self.imgdb.getImgCount(1))
        self.assertEqual(1,self.imgdb.savedbas(1,test_images_dir+"imgdb.data"))
        self.assertEqual(1,self.imgdb.resetdb(1))    
        self.assertEqual(1,self.imgdb.loaddb(1,test_images_dir+"imgdb.data"))
        self.assertEqual(1,self.imgdb.getImgCount(1))

    def testPopular(self):
        #TODO
        # make sure the shuffled sequence does not lose any elements        
        self.assertEqual(1,self.imgdb.addImage(1,test_images_dir+"DSC00006.JPG",6,))
        self.assertEqual(1,self.imgdb.addImage(1,test_images_dir+"DSC00007.JPG",7))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00008.JPG",8))
        self.assertEqual(3,self.imgdb.getImgCount(1))
 
    def testAddImage(self):
        # make sure the shuffled sequence does not lose any elements        
        self.assertEqual(1,self.imgdb.addImage(1,test_images_dir+"DSC00006.JPG",6,))
        self.assertEqual(1,self.imgdb.addImage(1,test_images_dir+"DSC00007.JPG",7))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00008.JPG",8))
        # add by blob
        fname = test_images_dir+"DSC00008.JPG"

        f = open(fname,'rb')
        data = f.read()
        f.close()

        self.assertEqual(1,self.imgdb.addImageBlob(1, data,9))

        assert self.imgdb.calcAvglDiff(1,8,9) == 0
        self.assertEqual(4,self.imgdb.getImgCount(1))
        
        self.assertEqual(1,self.imgdb.isImageOnDB(1,6))
        self.assertEqual(1,self.imgdb.isImageOnDB(1,7))
        self.assertEqual(1,self.imgdb.isImageOnDB(1,8))
        self.assertEqual(1,self.imgdb.isImageOnDB(1,9))
        self.assertEqual(0,self.imgdb.isImageOnDB(1,81))
    
    def testsaveloaddb(self):
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00006.JPG",6))
        self.assertEqual(1,self.imgdb.savedbas(1,test_images_dir+"imgdb.data"))
        self.assertEqual(1,self.imgdb.savedb(1))
        self.assertEqual(1,self.imgdb.resetdb(1))    
        self.assertEqual(1,self.imgdb.loaddb(1,test_images_dir+"imgdb.data"))
        self.assertEqual(1, self.imgdb.getImgCount(1))
        self.assertEqual(1, self.imgdb.isImageOnDB(1,6))        

    def testsaveandloadalldbs(self):
        import os
        dataFile = 'alternate.image.data'

        self.assertEqual(2,self.imgdb.createdb(2))
        self.assertEqual(3,self.imgdb.createdb(3))
        
        self.assertEqual(1,self.imgdb.resetdb(1))
        self.assertEqual(1,self.imgdb.resetdb(2))
        self.assertEqual(1,self.imgdb.resetdb(3))
        
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00006.JPG",6))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00007.JPG",7))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"Copy of DSC00006.JPG",8))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00019.JPG",19))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00021.JPG",21))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00021b.JPG",22))
        
        self.assertEqual(1,self.imgdb.addImage(2, test_images_dir+"DSC00006.JPG",6))
        self.assertEqual(1,self.imgdb.addImage(2, test_images_dir+"DSC00007.JPG",7))
        self.assertEqual(1,self.imgdb.addImage(2, test_images_dir+"Copy of DSC00006.JPG",8))
        
        self.assertEqual(1,self.imgdb.addImage(3, test_images_dir+"DSC00006.JPG",6))
        self.assertEqual(1,self.imgdb.addImage(3, test_images_dir+"DSC00007.JPG",7))
        self.assertEqual(1,self.imgdb.addImage(3, test_images_dir+"Copy of DSC00006.JPG",8))
        self.assertEqual(1,self.imgdb.addImage(3, test_images_dir+"DSC00019.JPG",19))
        self.assertEqual(1,self.imgdb.addImage(3, test_images_dir+"DSC00021.JPG",21))
        self.assertEqual(1,self.imgdb.addImage(3, test_images_dir+"DSC00021b.JPG",22))
        
        self.assertEqual(3,self.imgdb.savealldbs(dataFile))

        # reset
        self.assertEqual(1,self.imgdb.resetdb(1))
        self.assertEqual(1,self.imgdb.resetdb(2))
        self.assertEqual(1,self.imgdb.resetdb(3))

        self.assertEqual(0, self.imgdb.getImgCount(1))
        self.assertEqual(0, self.imgdb.getImgCount(2))
        self.assertEqual(0, self.imgdb.getImgCount(3))

        self.assertEqual(3,self.imgdb.loadalldbs(dataFile))
        
        self.assertEqual(6, self.imgdb.getImgCount(1))
        self.assertEqual(3, self.imgdb.getImgCount(2))
        self.assertEqual(6, self.imgdb.getImgCount(3))
        
    
    def testaddDir(self):
        self.assertEqual(16,self.imgdb.addDir(1,test_images_dir+"",True))
        self.assertEqual(16,self.imgdb.getImgCount(1))        
    
    def testremoveImg(self):
        self.assertEqual(1,self.imgdb.addImage(1,test_images_dir+"DSC00006.JPG",6))
        self.assertEqual(1,self.imgdb.addImage(1,test_images_dir+"DSC00007.JPG",7))
        self.assertEqual(2,self.imgdb.getImgCount(1))
        self.assertEqual(1,self.imgdb.isImageOnDB(1,6))
        self.assertEqual(1,self.imgdb.removeImg(1,6))
        self.assertEqual(1,self.imgdb.getImgCount(1))
        self.assertEqual(0,self.imgdb.isImageOnDB(1,6))
        
    def testcalcAvglDiff(self):
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00019.JPG",19))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00021.JPG",21))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00021b.JPG",22))
        self.assert_(self.imgdb.calcAvglDiff(1, 19,21) > 0.016)
        self.assert_(self.imgdb.calcAvglDiff(1, 22,21) < 0.016)

    def testcalcDiff(self):
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00019.JPG",19))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00021.JPG",21))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00021b.JPG",22))
        #TODO   
        
    def testgetImageDimensions(self):
        #TODO
        pass        
    def testgetImageAvgl(self):
        #TODO
        pass        
    def testgetImageAvgl(self):
        #TODO
        pass        
    def testgetImgIdList(self):
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00006.JPG",6))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00007.JPG",7))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"Copy of DSC00006.JPG",8))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00019.JPG",19))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00021.JPG",21))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00021b.JPG",22))
        
        dv = self.imgdb.getImgIdList(1)
        self.assert_(6 in dv)
        self.assert_(8 in dv)
        self.assert_(28 not in dv)
        self.assert_(22 in dv)
        
    def testgetDBList(self):
        self.assertEqual(2,self.imgdb.createdb(2))
        self.assertEqual(3,self.imgdb.createdb(3))
        self.assertEqual(1,self.imgdb.resetdb(1))
        self.assertEqual(1,self.imgdb.resetdb(2))
        self.assertEqual(1,self.imgdb.resetdb(3))
        
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00006.JPG",6))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00007.JPG",7))
        
        self.assertEqual(1,self.imgdb.addImage(2, test_images_dir+"DSC00006.JPG",6))
        self.assertEqual(1,self.imgdb.addImage(2, test_images_dir+"DSC00007.JPG",7))
        
        self.assertEqual(1,self.imgdb.addImage(3, test_images_dir+"DSC00006.JPG",6))
        self.assertEqual(1,self.imgdb.addImage(3, test_images_dir+"DSC00007.JPG",7))
        
        dblist = self.imgdb.getDBList()
        self.assert_(1 in dblist)
        self.assert_(2 in dblist)
        self.assert_(3 in dblist)
        self.assertEqual(3, len(dblist))
        
    def testgetQueryCount(self):
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00006.JPG",6))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00007.JPG",7))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"Copy of DSC00006.JPG",8))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00019.JPG",19))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00021.JPG",21))
        
        dv = self.imgdb.queryImgID(1,6, 4)
        dv = self.imgdb.queryImgID(1,7, 4)
        dv = self.imgdb.queryImgID(1,8, 4)
        dv = self.imgdb.queryImgID(1,21, 4)
        
        self.assertEqual(4, self.imgdb.getQueryCount(1))
        
    def testgetAddCount(self):
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00006.JPG",6))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00007.JPG",7))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"Copy of DSC00006.JPG",8))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00019.JPG",19))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00021.JPG",21))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00021b.JPG",22))

        self.assertEqual(6, self.imgdb.getAddCount(1))
        
    def testqueryImage(self):
        self.assertEqual(2,self.imgdb.createdb(2))
        self.assertEqual(3,self.imgdb.createdb(3))
        self.assertEqual(1,self.imgdb.resetdb(1))
        self.assertEqual(1,self.imgdb.resetdb(2))
        self.assertEqual(1,self.imgdb.resetdb(3))
        
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00006.JPG",6))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00007.JPG",7))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"Copy of DSC00006.JPG",8))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00019.JPG",19))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00021.JPG",21))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00021b.JPG",22))
        
        self.assertEqual(1,self.imgdb.addImage(2, test_images_dir+"DSC00006.JPG",6))
        self.assertEqual(1,self.imgdb.addImage(2, test_images_dir+"DSC00007.JPG",7))
        self.assertEqual(1,self.imgdb.addImage(2, test_images_dir+"Copy of DSC00006.JPG",8))
        
        self.assertEqual(1,self.imgdb.addImage(3, test_images_dir+"DSC00006.JPG",6))
        self.assertEqual(1,self.imgdb.addImage(3, test_images_dir+"DSC00007.JPG",7))
        self.assertEqual(1,self.imgdb.addImage(3, test_images_dir+"Copy of DSC00006.JPG",8))
        self.assertEqual(1,self.imgdb.addImage(3, test_images_dir+"DSC00019.JPG",19))
        self.assertEqual(1,self.imgdb.addImage(3, test_images_dir+"DSC00021.JPG",21))
        self.assertEqual(1,self.imgdb.addImage(3, test_images_dir+"DSC00021b.JPG",22))
        
        dv = self.imgdb.queryImgID(1,6, 4)
        self.assertEqual(5, len(dv))
       
        # are image clones really scoring as very similar?
        dv = self.imgdb.queryImgID(1,6, 3)
        self.assertEqual(4, len(dv))
        self.assertEqual(8, dv[0][0]) 
        self.assertEqual(6, dv[1][0])
        self.assertEqual(19, dv[2][0]) 

        # query by path
        dv = self.imgdb.queryImgPath(1,test_images_dir+"DSC00007.JPG", 3)
        self.assertEqual(4, len(dv))
        self.assertEqual(7, dv[0][0]) 
            # fast
        dv = self.imgdb.queryImgPath(1,test_images_dir+"DSC00007.JPG", 3,0,True)
        self.assertEqual(4, len(dv))
        self.assertEqual(7, dv[0][0]) 
            # sketch
        dv = self.imgdb.queryImgPath(1,test_images_dir+"DSC00007.JPG", 3,1)
        self.assertEqual(4, len(dv))
        self.assertEqual(7, dv[0][0]) 

        # query non existing
        dv = self.imgdb.queryImgID(2,1139, 4)
        self.assertEqual(0, len(dv))

        # query by blob
        fname = test_images_dir+"DSC00007.JPG"

        f = open(fname,'rb')
        data = f.read()
        f.close()

        dv = self.imgdb.queryImgBlob(1,data, 3)
        self.assertEqual(4, len(dv))
        self.assertEqual(7, dv[0][0]) 
       
        # test Fast search
        dv = self.imgdb.queryImgID(3,21, 4, True)
        self.assertEqual(5, len(dv))
        self.assertEqual(21, dv[0][0]) 
        self.assertEqual(22, dv[1][0])
        self.assertEqual(19, dv[2][0])
        self.assertEqual(7, dv[3][0]) 
        
        dv = self.imgdb.queryImgID(3,6, 2)
        self.assertEqual(3, len(dv))
        self.assertEqual(6, dv[0][0]) 
        self.assertEqual(8, dv[1][0])         
 
    def testgetImageHeight(self):
        pass

        #int getImageHeight(const int dbId, long int id);
        #int getImageWidth(const int dbId, long int id);
    def testaddImageBlob(self):
        pass

        #int addImageBlob(const int dbId, const long int id, const void *blob, const long length);
    def testisValidDB(self):
        self.assertEqual(True, self.imgdb.isValidDB(1))
        self.assertEqual(False, self.imgdb.isValidDB(1311))

    def testdestroydb(self):
        pass
        #int destroydb(const int dbId);
    def testremovedb(self):
        pass
        #bool removedb(const int dbId);

#// keywords in images
    def testremoveKeywordImg(self):
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00021b.JPG",1))
        self.imgdb.addKeywordImg(1,1,2)
        kwds = self.imgdb.getKeywordsImg(1,1)
        self.assert_(2 in kwds)
        self.imgdb.removeKeywordImg(1,1,2)
        kwds = self.imgdb.getKeywordsImg(1,1)
        self.assertEqual(0, len(kwds))

    def testremoveAllKeywordImg(self):
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00021b.JPG",1))
        self.imgdb.addKeywordImg(1,1,2)
        self.imgdb.removeAllKeywordImg(1, 1);
        kwds = self.imgdb.getKeywordsImg(1,1)
        self.assertEqual(0, len(kwds))

#// query by keywords
    def testqueryImgIDKeywords(self):
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00006.JPG",6))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00007.JPG",7))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"Copy of DSC00006.JPG",8))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00019.JPG",19))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00021.JPG",21))
        self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00021b.JPG",22))
        
        self.imgdb.addKeywordImg(1,6,2)
        self.imgdb.addKeywordImg(1,7,3)
        self.imgdb.addKeywordImg(1,7,2)

        #std::vector<double> queryImgIDKeywords(const int dbId, long int id, int numres, int kwJoinType, int_vector keywords){
        #dv [[8L, 100], [6L, 100], [19L, 15.272009339950403], [22L, 14.274818233138154], [7L, 14.086848507770208]]

        dv = self.imgdb.queryImgIDKeywords(1,6, 4, 1, [2,3],False) # AND
        ids = [r[0] for r in dv]
        print ids
        self.assert_(7 in ids)
        self.assertEqual(1,len(dv))

        dv = self.imgdb.queryImgIDKeywords(1,6, 4, 0, [2,3],True) # OR
        ids = [r[0] for r in dv]
        print ids
        self.assert_(7 in ids)
        self.assert_(6 in ids)
        self.assertEqual(2,len(dv))

        dv = self.imgdb.queryImgIDKeywords(1,6, 4, 1, [3])
        ids = [r[0] for r in dv]
        print ids
        self.assert_(7 in ids)
        self.assertEqual(1,len(dv))
    
        # no keywords
        dv = self.imgdb.queryImgIDKeywords(1,6, 4, 1, [])
        ids = [r[0] for r in dv]
        print ids
        print dv
        self.assertEqual(0,len(dv))

        # random keywords
        dv = self.imgdb.queryImgIDKeywords(1,0, 4, 1, [3])
        ids = [r[0] for r in dv]
        print ids
        self.assert_(7 in ids)
        self.assertEqual(1,len(dv))

    def testqueryImgIDFastKeywords(self):
        pass
        #std::vector<double> queryImgIDFastKeywords(const int dbId, long int id, int numres, int kwJoinType, std::vector<int> keywords);
    def testtAllImgsByKeywords(self):
        pass
        #std::vector<long int> getAllImgsByKeywords(const int dbId, const int numres, int kwJoinType, std::vector<int> keywords);
    def testgetKeywordsVisualDistance(self):
        pass
        #double getKeywordsVisualDistance(const int dbId, int distanceType, std::vector<int> keywords);
    
if __name__ == '__main__':
    unittest.main()
