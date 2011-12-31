#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

###############################################################################
# begin				   : 2008-12-04
# copyright			   : Ricardo Niederberger Cabral
# email				   : ricardo dot cabral at imgseek dot net
###############################################################################
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA	02111-1307	USA
#
###############################################################################

import unittest
from ImageDB import ImgDB 

test_images_dir = '../test/data/'

class ImageDBTest(unittest.TestCase):
	
	def setUp(self):
		self.imgdb = ImgDB()
		self.assertEqual(1,self.imgdb.createdb(1))
		self.assertEqual(1,self.imgdb.resetdb(1))

	def tearDown(self):
		self.assertEqual(1,self.imgdb.resetdb(1));
		self.imgdb.closedb();		 

	def testAddImage(self):
		# make sure the shuffled sequence does not lose any elements		
		self.assertEqual(1,self.imgdb.addImage(1,test_images_dir+"DSC00006.JPG",6,))
		self.assertEqual(1,self.imgdb.addImage(1,test_images_dir+"DSC00007.JPG",7))
		self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00008.JPG",8))
		self.assertEqual(3,self.imgdb.getImgCount(1))
		
		self.assertEqual(1,self.imgdb.isImageOnDB(1,6))
		self.assertEqual(1,self.imgdb.isImageOnDB(1,7))
		self.assertEqual(1,self.imgdb.isImageOnDB(1,8))
		self.assertEqual(0,self.imgdb.isImageOnDB(1,81))
	
	"""
		self.assertEqual(self.seq, range(10))
		self.assert_(element in self.seq)
	"""
	
	def testsaveloaddb(self):
		self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00006.JPG",6))
		self.assertEqual(1,self.imgdb.savedbas(1,test_images_dir+"imgdb.data"))
		self.assertEqual(1,self.imgdb.resetdb(1))	 
		self.assertEqual(1,self.imgdb.loaddb(1,test_images_dir+"imgdb.data"))
		self.assertEqual(1, self.imgdb.getImgCount(1))
		self.assertEqual(1, self.imgdb.isImageOnDB(1,6))		

	def testsaveandloadalldbs(self):
		import os
		#dataFile = "c:\\data\\imgdb.all"
		dataFile = os.path.expanduser("~/isk-db").replace('/','\\')
		
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
		
		self.assertEqual(1,self.imgdb.savealldbs(dataFile))

		# reset
		self.assertEqual(1,self.imgdb.resetdb(1))
		self.assertEqual(1,self.imgdb.resetdb(2))
		self.assertEqual(1,self.imgdb.resetdb(3))

		self.assertEqual(0, self.imgdb.getImgCount(1))
		self.assertEqual(0, self.imgdb.getImgCount(2))
		self.assertEqual(0, self.imgdb.getImgCount(3))

		self.assertEqual(1,self.imgdb.loadalldbs(dataFile))
		
		self.assertEqual(6, self.imgdb.getImgCount(1))
		self.assertEqual(3, self.imgdb.getImgCount(2))
		self.assertEqual(6, self.imgdb.getImgCount(3))
		
	
	def testaddDir(self):
		self.assertEqual(15,self.imgdb.addDir(1,test_images_dir+"",True))
		self.assertEqual(15,self.imgdb.getImgCount(1))		  
	
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
		
	def testgetImageDimensions(self):
		pass		
	def testgetImageAvgl(self):
		pass		
	def testgetImageAvgl(self):
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
		self.assertEqual(1,self.imgdb.addImage(1, test_images_dir+"DSC00021b.JPG",22))
		
		dv = self.imgdb.queryImgID(1,6, 4)
		self.assertEqual(4, len(dv))

		dv = self.imgdb.queryImgID(1,7, 4)
		self.assertEqual(4, len(dv))

		dv = self.imgdb.queryImgID(1,8, 4)
		self.assertEqual(4, len(dv))

		dv = self.imgdb.queryImgID(1,21, 4)
		self.assertEqual(4, len(dv))
		
		self.assertEqual(4, self.imgdb.getQueryCount(1))
		
	def testgetAddCount(self):
		#TODO
		pass		
		
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
		self.assertEqual(4, len(dv))
		
		dv = self.imgdb.queryImgID(1,6, 3)
		self.assertEqual(3, len(dv))
		self.assertEqual(6, dv[0][0]) 
		self.assertEqual(19, dv[1][0])
		self.assertEqual(7, dv[2][0]) 
				
		dv = self.imgdb.queryImgID(2,19, 4)
		self.assertEqual(0, len(dv))
		
		dv = self.imgdb.queryImgID(3,21, 4)
		self.assertEqual(4, len(dv))
		self.assertEqual(22, dv[0][0]) 
		self.assertEqual(19, dv[1][0])
		self.assertEqual(7, dv[2][0])
		self.assertEqual(8, dv[3][0]) 
		
		dv = self.imgdb.queryImgID(3,6, 2)
		self.assertEqual(2, len(dv))
		self.assertEqual(8, dv[0][0]) 
		self.assertEqual(19, dv[1][0])		   
	
if __name__ == '__main__':
	unittest.main()
