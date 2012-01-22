/******************************************************************************
imgSeek ::  C++ database implementation
---------------------------------------
begin                : Fri Jan 17 2003
email                : nieder|at|mail.ru

Copyright (C) 2003-2009 Ricardo Niederberger Cabral

Clean-up and speed-ups by Geert Janssen <geert at ieee.org>, Jan 2006:
- removed lots of dynamic memory usage
- SigStruct now holds only static data
- db save and load much faster
- made Qt image reading faster using scanLine()
- simpler imgBin initialization
- corrected pqResults calculation; did not get best scores

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 ******************************************************************************/

/* C Includes */
#include <ctime>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

/* STL Includes */
#include <fstream>
#include <iostream>

using namespace std;
/* ImageMagick includes */
#include <magick/api.h>

/* imgSeek includes */

/* Database */
#include "bloom_filter.h"
#include "imgdb.h"

//TODO reactivate fast jpeg loader: http://trac.xapian.org/browser/branches/imgseek/xapian-extras/imgseek

// Globals
dbSpaceMapType dbSpace;
keywordsMapType globalKwdsMap;

/* Fixed weight mask for pixel positions (i,j).
Each entry x = i*NUM_PIXELS + j, gets value max(i,j) saturated at 5.
To be treated as a constant.
 */
unsigned char imgBin[16384];
int imgBinInited = 0;

// Macros
#define validate_dbid(dbId) (dbSpace.count(dbId))
#define validate_imgid(dbId, imgId) (dbSpace.count(dbId) && (dbSpace[dbId]->sigs.count(imgId)))

void initImgBin()
{
	imgBinInited = 1;
	srand((unsigned)time(0));

	/* setup initial fixed weights that each coefficient represents */
	int i, j;

	/*
	0 1 2 3 4 5 6 i
	0 0 1 2 3 4 5 5
	1 1 1 2 3 4 5 5
	2 2 2 2 3 4 5 5
	3 3 3 3 3 4 5 5
	4 4 4 4 4 4 5 5
	5 5 5 5 5 5 5 5
	5 5 5 5 5 5 5 5
	j
	 */

	/* Every position has value 5, */
	memset(imgBin, 5, NUM_PIXELS_SQUARED);

	/* Except for the 5 by 5 upper-left quadrant: */
	for (i = 0; i < 5; i++)
		for (j = 0; j < 5; j++)
			imgBin[i * 128 + j] = max(i, j);
	// Note: imgBin[0] == 0

}

void initDbase(const int dbId) {
	/* should be called before adding images */
	if (!imgBinInited) initImgBin();

	if (dbSpace.count(dbId))  { // db id already used?
		cerr << "ERROR: dbId already in use" << endl;
		return;
	}
	dbSpace[dbId] = new dbSpaceStruct();
}

void closeDbase() {
	/* should be called before exiting app */
	for (dpspaceIterator it = dbSpace.begin(); it != dbSpace.end(); it++) {
		resetdb((*it).first);
        delete (*it).second;
	}
}

int getImageWidth(const int dbId, long int id) {
	if (!validate_imgid(dbId, id)) { cerr << "ERROR: image id (" << id << ") not found on given dbid (" << dbId << ") or dbid not existant" << endl ; return 0;};
	return dbSpace[dbId]->sigs[id]->width;
}

bool isImageOnDB(const int dbId, long int id) {
	if (!validate_dbid(dbId)) { cerr << "ERROR: database space not found (" << dbId << ")" << endl; return false;}
	return dbSpace[dbId]->sigs.count(id) > 0;
}

int getImageHeight(const int dbId, long int id) {
	if (!validate_imgid(dbId, id)) { cerr << "ERROR: image id (" << id << ") not found on given dbid (" << dbId << ") or dbid not existant" << endl ; return 0;};
	return dbSpace[dbId]->sigs[id]->height;
}

double_vector getImageAvgl(const int dbId, long int id) {
	double_vector res;
	if (!validate_dbid(dbId)) { cerr << "ERROR: database space not found (" << dbId << ")" << endl; return res; }

	if (!dbSpace[dbId]->sigs.count(id))
		return res;
	for(int i=0;i<3; i++) {
		res.push_back(dbSpace[dbId]->sigs[id]->avgl[i]);
	}
	return res;
}

int addImageFromImage(const int dbId, const long int id, Image * image ) {

	/* id is a unique image identifier
	filename is the image location
	thname is the thumbnail location for this image
	doThumb should be set to 1 if you want to save the thumbnail on thname
	Images with a dimension smaller than ignDim are ignored
	 */
	if (!validate_dbid(dbId)) { cerr << "ERROR: database space not found (" << dbId << ")" << endl; return 0; }

    if (image == (Image *) NULL) {
    	cerr << "ERROR: unable to add null image" << endl;
    	return 0;
    }

	// Made static for speed; only used locally
	static Unit cdata1[16384];
	static Unit cdata2[16384];
	static Unit cdata3[16384];
	int i;
	int width, height;

	ExceptionInfo exception;

	Image *resize_image;

	/*
	Initialize the image info structure and read an image.
	 */
	GetExceptionInfo(&exception);

	width = image->columns;
	height = image->rows;

	resize_image = SampleImage(image, 128, 128, &exception);

	DestroyImage(image);

	DestroyExceptionInfo(&exception);

	if (resize_image == (Image *) NULL) {
		cerr << "ERROR: unable to resize image" << endl;
		return 0;
	}

    // store color value for basic channels
	unsigned char rchan[16384];
	unsigned char gchan[16384];
	unsigned char bchan[16384];

	GetExceptionInfo(&exception);

	const PixelPacket *pixel_cache = AcquireImagePixels(resize_image, 0, 0, 128, 128, &exception);

	for (int idx = 0; idx < 16384; idx++) {
		rchan[idx] = pixel_cache->red;
		gchan[idx] = pixel_cache->green;
		bchan[idx] = pixel_cache->blue;
		pixel_cache++;
	}

    DestroyImage(resize_image);

	transformChar(rchan, gchan, bchan, cdata1, cdata2, cdata3);

	DestroyExceptionInfo(&exception);

	SigStruct *nsig = new SigStruct();
	nsig->id = id;
	nsig->width = width;
	nsig->height = height;

	if (dbSpace[dbId]->sigs.count(id)) {
		delete dbSpace[dbId]->sigs[id];
		dbSpace[dbId]->sigs.erase(id);

		cerr << "ERROR: dbId already in use" << endl;
		return 0;

	}
	// insert into sigmap
	dbSpace[dbId]->sigs[id] = nsig;
	// insert into ids bloom filter
	dbSpace[dbId]->imgIdsFilter->insert(id);

	calcHaar(cdata1, cdata2, cdata3,
			nsig->sig1, nsig->sig2, nsig->sig3, nsig->avgl);

	for (i = 0; i < NUM_COEFS; i++) {	// populate buckets


#ifdef FAST_POW_GEERT
		int x, t;
		// sig[i] never 0
		int x, t;

		x = nsig->sig1[i];
		t = (x < 0);		/* t = 1 if x neg else 0 */
		/* x - 0 ^ 0 = x; i - 1 ^ 0b111..1111 = 2-compl(x) = -x */
		x = (x - t) ^ -t;
		dbSpace[dbId]->imgbuckets[0][t][x].push_back(id);

		x = nsig->sig2[i];
		t = (x < 0);
		x = (x - t) ^ -t;
		dbSpace[dbId]->imgbuckets[1][t][x].push_back(id);

		x = nsig->sig3[i];
		t = (x < 0);
		x = (x - t) ^ -t;
		dbSpace[dbId]->imgbuckets[2][t][x].push_back(id);

		should not fail

#else //FAST_POW_GEERT
		//long_array3 imgbuckets = dbSpace[dbId]->imgbuckets;
		if (nsig->sig1[i]>0) dbSpace[dbId]->imgbuckets[0][0][nsig->sig1[i]].push_back(id);
		if (nsig->sig1[i]<0) dbSpace[dbId]->imgbuckets[0][1][-nsig->sig1[i]].push_back(id);

		if (nsig->sig2[i]>0) dbSpace[dbId]->imgbuckets[1][0][nsig->sig2[i]].push_back(id);
		if (nsig->sig2[i]<0) dbSpace[dbId]->imgbuckets[1][1][-nsig->sig2[i]].push_back(id);

		if (nsig->sig3[i]>0) dbSpace[dbId]->imgbuckets[2][0][nsig->sig3[i]].push_back(id);
		if (nsig->sig3[i]<0) dbSpace[dbId]->imgbuckets[2][1][-nsig->sig3[i]].push_back(id);

#endif //FAST_POW_GEERT

	}

	// success after all
	return 1;

}

int addImageBlob(const int dbId, const long int id, const char *blob, const long length) {

	ExceptionInfo exception;
	GetExceptionInfo(&exception);

	ImageInfo *image_info;
	image_info = CloneImageInfo((ImageInfo *) NULL);

	Image *image = BlobToImage(image_info, blob, length, &exception);
	if (exception.severity != UndefinedException) CatchException(&exception);

	DestroyImageInfo(image_info);
	return addImageFromImage(dbId, id, image);
}

int addImage(const int dbId, const long int id, char *filename) {

//	if (dbSpace[dbId]->sigs.count(id)) { // image already in db
//		return 0;
//	}

	//TODO update image: remove old, add new

	ExceptionInfo exception;
	GetExceptionInfo(&exception);

	ImageInfo *image_info;
	image_info = CloneImageInfo((ImageInfo *) NULL);
	(void) strcpy(image_info->filename, filename);
	Image *image = ReadImage(image_info, &exception);
	if (exception.severity != UndefinedException) CatchException(&exception);
	DestroyImageInfo(image_info);
	DestroyExceptionInfo(&exception);

	if (image == (Image *) NULL) {
    	cerr << "ERROR: unable to read image" << endl;
    	return 0;
    }

	return addImageFromImage(dbId, id, image);
}

int loaddbfromstream(const int dbId, std::ifstream& f, srzMetaDataStruct& md) {

	if (!dbSpace.count(dbId))  { // haven't been inited yet
		initDbase(dbId);
	} else { // already exists, so reset first
		resetdb(dbId);
	}

	long int id;
	int sz;
	// read buckets
	for (int c = 0; c < 3; c++)
		for (int pn = 0; pn < 2; pn++)
			for (int i = 0; i < 16384; i++) {
				f.read((char *) &(sz), sizeof(int));
				if (!f.good()) {
					continue;
				}
				for (int k = 0; k < sz; k++) {
					f.read((char *) &(id), sizeof(long int));
					if (!f.good()) {
						cerr << "ERROR bad file while reading id" << endl;
						continue;
					}
					dbSpace[dbId]->imgbuckets[c][pn][i].push_back(id);
				}
			}

	// read sigs
	sigMap::size_type szt;
	f.read((char *) &(szt), sizeof(sigMap::size_type));
	if (!f.good()) {
		cerr << "ERROR bad file while reading sigs size" << endl;
		return 0;
	}

	if (md.iskVersion < SRZ_V0_6_0) {
		cout << "INFO migrating database from a version prior to 0.6" << endl;
		// read sigs
		for (int k = 0; k < szt; k++) {
			sigStructV06* nsig06 = new sigStructV06();
			f.read((char *) nsig06, sizeof(sigStructV06));
			SigStruct* nsig = new SigStruct(nsig06);
			dbSpace[dbId]->sigs[nsig->id]=nsig;
		}
		return 1;

	} else { // current version

		DiskSigStruct* ndsig = new DiskSigStruct();
		for (int k = 0; k < szt; k++) {

			f.read((char *) ndsig, sizeof(DiskSigStruct));
			if (!f.good()) {
				cerr << "ERROR bad file while reading diskSigStruct" << endl;
				return 0;
			}
			SigStruct* nsig = new SigStruct(ndsig);
			// insert new sig
			dbSpace[dbId]->sigs[nsig->id]=nsig;
			// insert into ids bloom filter
			dbSpace[dbId]->imgIdsFilter->insert(nsig->id);
			// read kwds
			int kwid;
			int szk;
			f.read((char *) &(szk), sizeof(int));
			if (!f.good()) {
				cerr << "ERROR bad file while reading number of kwds" << endl;
				return 0;
			}

			for (int ki = 0; ki < szk; ki++) {
				f.read((char *) &(kwid), sizeof(int));
				if (!f.good()) {
					cerr << "ERROR bad file while reading kwd id" << endl;
					return 0;
				}
				nsig->keywords.insert(kwid);
				// populate keyword postings
				getKwdPostings(kwid)->imgIdsFilter->insert(nsig->id);
			}
		}
		delete ndsig;
		return 1;
	}
}

srzMetaDataStruct loadGlobalSerializationMetadata(std::ifstream& f) {

	srzMetaDataStruct md;

	// isk version
	f.read((char *) &(md.iskVersion), sizeof(int));
	if (!f.good()) {
		cerr << "ERROR bad file while reading isk version" << endl;
		return md;
	}

	// binding language
	f.read((char *) &(md.bindingLang), sizeof(int));
	if (!f.good()) {
		cerr << "ERROR bad file while reading lang" << endl;
		return md;
	}

    // trial or full
    if (md.iskVersion < SRZ_V0_7_0) {
    	f.read((char *) &(md.isTrial), sizeof(int));
    }

	// platform
	f.read((char *) &(md.compilePlat), sizeof(int));
	if (!f.good()) {
		cerr << "ERROR bad file while reading platf" << endl;
		return md;
	}

	// ok, I have some valid metadata
	md.isValidMetadata = 1;

	return md;
}

int loaddb(const int dbId, char *filename) {
	std::ifstream f(filename, ios::binary);
	if (!f.is_open()) {
		cerr << "ERROR: unable to open file for read ops:" << filename << endl;
		return 0;


	}

	int isMetadata = f.peek();

	srzMetaDataStruct md;
	md.isValidMetadata = 0;

	if (isMetadata == SRZ_VERSIONED) { // has metadata
		f.read((char *) &(isMetadata), sizeof(int));
		if (!f.good()) {
			cerr << "ERROR bad file while reading is meta" << endl;
			return 0;
		}

		md = loadGlobalSerializationMetadata(f);
	}

	int res = loaddbfromstream(dbId, f, md);

	f.close();
	return res;
}

int loadalldbs(char* filename) {
	std::ifstream f(filename, ios::binary);

	if (!f.is_open()) { // file not found, perhaps its the first start
		return 0;
	}

	int isMetadata = f.peek();

	srzMetaDataStruct md;
	md.isValidMetadata = 0;

	if (isMetadata == SRZ_VERSIONED) {// has metadata
		f.read((char *) &(isMetadata), sizeof(int));
		if (!f.good()) {
			cerr << "ERROR bad file while reading is meta 2" << endl;
			return 0;
		}

		if (isMetadata != SRZ_VERSIONED) {
			cerr << "ERROR: peek diff read" << endl;
			return 0;
		}
		md = loadGlobalSerializationMetadata(f);
	}

	int dbId = 1;
	int res = 0;
	int sz = 0;

	f.read((char *) &(sz), sizeof(int)); // number of dbs
	if (!f.good()) {
		cerr << "ERROR bad file while reading num dbs" << endl;
		return 0;
	}

	for (int k = 0; k < sz; k++) { // for each db
		f.read((char *) &(dbId), sizeof(int)); // db id
		if (!f.good()) {
			cerr << "ERROR bad file while reading db id" << endl;
			return 0;
		}
		res += loaddbfromstream(dbId, f, md);
	}

	f.close();
	return res;
}

int savedbtostream(const int dbId, std::ofstream& f) {
	/*
	Serialization order:
	for each color {0,1,2}:
	for {positive,negative}:
	for each 128x128 coefficient {0-16384}:
	[int] bucket size (size of list of ids)
	for each id:
	[long int] image id
	[int] number of images (signatures)
	for each image:
	[long id] image id
	for each sig coef {0-39}:  (the NUM_COEFS greatest coefs)
	for each color {0,1,2}:
	[int] coef index (signed)
	for each color {0,1,2}:
	[double] average luminance
	[int] image width
	[int] image height

	 */
	int sz;
	long int id;

	if (!validate_dbid(dbId)) { cerr << "ERROR: database space not found (" << dbId << ")" << endl; return 0;}

	// save buckets
	for (int c = 0; c < 3; c++) {
		for (int pn = 0; pn < 2; pn++) {
			for (int i = 0; i < 16384; i++) {
				sz = dbSpace[dbId]->imgbuckets[c][pn][i].size();

				f.write((char *) &(sz), sizeof(int));
				long_listIterator end = dbSpace[dbId]->imgbuckets[c][pn][i].end();
				for (long_listIterator it = dbSpace[dbId]->imgbuckets[c][pn][i].begin(); it != end; it++) {
					f.write((char *) &((*it)), sizeof(long int));
				}
			}
		}
	}

	// save sigs
	sigMap::size_type szt = dbSpace[dbId]->sigs.size();

	f.write((char *) &(szt), sizeof(sigMap::size_type));

	for (sigIterator it = dbSpace[dbId]->sigs.begin(); it != dbSpace[dbId]->sigs.end(); it++) {
		id = (*it).first;
		SigStruct* sig = (SigStruct*) (it->second);
		DiskSigStruct dsig(*sig);
		f.write((char *) (&dsig), sizeof(DiskSigStruct));

		//// keywords
		int_hashset& kwds = sig->keywords;
		sz = kwds.size();
		// number of keywords
		f.write((char *) &(sz), sizeof(int));
		// dump keywds
		int kwid;
		for (int_hashset::iterator itkw = kwds.begin(); itkw != kwds.end(); itkw++) {
			kwid = *itkw;
			f.write((char *) &(kwid), sizeof(int));
		}
	}

	return 1;
}

void saveGlobalSerializationMetadata(std::ofstream& f) {

	int wval;

	// is versioned
	wval = SRZ_VERSIONED;
	f.write((char*)&(wval), sizeof(int));

	// isk version
	wval = SRZ_CUR_VERSION;
	f.write((char*)&(wval), sizeof(int));

	// binding language
#ifdef ISK_SWIG_JAVA
	wval = SRZ_LANG_JAVA;
	f.write((char*)&(wval), sizeof(int));
#else
	wval = SRZ_LANG_PYTHON;
	f.write((char*)&(wval), sizeof(int));
#endif

	// platform
#ifdef _WINDOWS
	wval = SRZ_PLAT_WINDOWS;
	f.write((char*)&(wval), sizeof(int));
#else
	wval = SRZ_PLAT_LINUX;
	f.write((char*)&(wval), sizeof(int));
#endif
}

int savedb(const int dbId, char *filename) {
	std::ofstream f(filename, ios::binary);
	if (!f.is_open()) {
		cerr << "ERROR: error opening file for write ops" << endl;
		return 0;


	}

	saveGlobalSerializationMetadata(f);

	int res = savedbtostream( dbId, f);
	f.close();
	return res;
}

int savealldbs(char* filename) {
	std::ofstream f(filename, ios::binary);
	if (!f.is_open()) {
		cerr << "ERROR: error opening file for write ops" << endl;
		return 0;
	}

	saveGlobalSerializationMetadata(f);

	int res = 0;
	int sz = dbSpace.size();
	f.write((char *) &(sz), sizeof(int)); // num dbs
	int dbId;

	for (dpspaceIterator it = dbSpace.begin(); it != dbSpace.end(); it++) {
		dbId = (*it).first;
		f.write((char *) &(dbId), sizeof(int)); // db id
		res += savedbtostream( dbId, f);
	}

	f.close();
	return res;
}

std::vector<double> queryImgDataFiltered(const int dbId, Idx * sig1, Idx * sig2, Idx * sig3, double *avgl, int numres, int sketch, bloom_filter* bfilter, bool colorOnly) {
	int idx, c;
	int pn;
	Idx *sig[3] = { sig1, sig2, sig3 };

	if (bfilter) { // make sure images not on filter are penalized
		for (sigIterator sit = dbSpace[dbId]->sigs.begin(); sit != dbSpace[dbId]->sigs.end(); sit++) {

			if (!bfilter->contains((*sit).first)) { // image doesnt have keyword, just give it a terrible score
				(*sit).second->score = 99999999;
			} else { // ok, image content should be taken into account
				(*sit).second->score = 0;
				for (c = 0; c < 3; c++) {
					(*sit).second->score += weights[sketch][0][c] * fabs((*sit).second->avgl[c] - avgl[c]);
				}
			}
		}
		delete bfilter;

	} else { // search all images
		for (sigIterator sit = dbSpace[dbId]->sigs.begin(); sit != dbSpace[dbId]->sigs.end(); sit++) {
			(*sit).second->score = 0;
			for (c = 0; c < 3; c++) {
				(*sit).second->score += weights[sketch][0][c] * fabs((*sit).second->avgl[c] - avgl[c]);
			}
		}
	}
    if (!colorOnly) {
        for (int b = 0; b < NUM_COEFS; b++) {	// for every coef on a sig
            for (c = 0; c < 3; c++) {
                //TODO see if FAST_POW_GEERT gives the same results
#ifdef FAST_POW_GEERT
                pn  = sig[c][b] < 0;
                idx = (sig[c][b] - pn) ^ -pn;
#else
                pn = 0;
                if (sig[c][b]>0) {
                    pn = 0;
                    idx = sig[c][b];
                } else {
                    pn = 1;
                    idx = -sig[c][b];
                }
#endif

                // update the score of every image which has this coef
                long_listIterator end = dbSpace[dbId]->imgbuckets[c][pn][idx].end();
                for (long_listIterator uit = dbSpace[dbId]->imgbuckets[c][pn][idx].begin();
                uit != end; uit++) {
                    //TODO in each iteration search in tree (std::map) is performed. i think the better way to link by pointers.
                    dbSpace[dbId]->sigs[(*uit)]->score -= weights[sketch][imgBin[idx]][c];
                }
            }
        }
    }

	sigPriorityQueue pqResults;		/* results priority queue; largest at top */

	sigIterator sit = dbSpace[dbId]->sigs.begin();

	vector<double> V;

	// Fill up the numres-bounded priority queue (largest at top):
	for (int cnt = 0; cnt < numres; cnt++) {
		if (sit == dbSpace[dbId]->sigs.end()) {
			// No more images; cannot get requested numres, so just return these initial ones.
			return V;
		}
		pqResults.push(*(*sit).second);
		sit++;
	}


	for (; sit != dbSpace[dbId]->sigs.end(); sit++) {
		// only consider if not ignored due to keywords and if is a better match than the current worst match
		if (((*sit).second->score < 99999) && ((*sit).second->score < pqResults.top().score)) {
			// Make room by dropping largest entry:
			pqResults.pop();
			// Insert new entry:
			pqResults.push(*(*sit).second);
		}
	}

	SigStruct curResTmp;            /* current result waiting to be returned */
	while (pqResults.size()) {
		curResTmp = pqResults.top();
		pqResults.pop();
		if (curResTmp.score < 99999) {
			V.insert(V.end(), curResTmp.id);
			V.insert(V.end(), curResTmp.score);
		}
	}

	return V;
}


/* sig1,2,3 are int arrays of length NUM_COEFS
avgl is the average luminance
numres is the max number of results
sketch (0 or 1) tells which set of weights to use
 */
std::vector<double> queryImgData(const int dbId, Idx * sig1, Idx * sig2, Idx * sig3, double *avgl, int numres, int sketch, bool colorOnly) {
	return queryImgDataFiltered(dbId, sig1, sig2, sig3, avgl, numres, sketch, 0, colorOnly);

}

/* sig1,2,3 are int arrays of lenght NUM_COEFS
avgl is the average luminance
thresd is the limit similarity threshold. Only images with score > thresd will be a result
`sketch' tells which set of weights to use
sigs is the source to query on (map of signatures)
every search result is removed from sigs. (right now this functn is only used by clusterSim)
 */
long_list queryImgDataForThres(const int dbId, sigMap * tsigs,
		Idx * sig1, Idx * sig2, Idx * sig3,
		double *avgl, float thresd, int sketch) {
	int idx, c;
	int pn;
	long_list res;
	Idx *sig[3] = { sig1, sig2, sig3 };

	if (!validate_dbid(dbId)) { cerr << "ERROR: database space not found (" << dbId << ")" << endl; return res;}

	for (sigIterator sit = (*tsigs).begin(); sit != (*tsigs).end(); sit++) {
		(*sit).second->score = 0;
		for (c = 0; c < 3; c++)
			(*sit).second->score += weights[sketch][0][c]
			                                           * fabs((*sit).second->avgl[c] - avgl[c]);
	}
	for (int b = 0; b < NUM_COEFS; b++) {	// for every coef on a sig
		for (c = 0; c < 3; c++) {
#ifdef FAST_POW_GEERT  //TODO is it faster? same results? remove this code?
			pn  = sig[c][b] < 0;
			idx = (sig[c][b] - pn) ^ -pn;
#else
			pn = 0;
			if (sig[c][b]>0) {
				pn = 0;
				idx = sig[c][b];
			} else {
				pn = 1;
				idx = -sig[c][b];
			}
#endif
			// update the score of every image which has this coef
			//TODO in each iteration search in tree (std::map) is performed. i think the better way to link by pointers.
			long_listIterator end = dbSpace[dbId]->imgbuckets[c][pn][idx].end();
			for (long_listIterator uit = dbSpace[dbId]->imgbuckets[c][pn][idx].begin();
			uit != end; uit++) {
				if ((*tsigs).count((*uit)))
					// this is an ugly line
					(*tsigs)[(*uit)]->score -=
						weights[sketch][imgBin[idx]][c];
			}
		}
	}
	for (sigIterator sit = (*tsigs).begin(); sit != (*tsigs).end(); sit++) {
		if ((*sit).second->score < thresd) {
			res.push_back((*sit).second->id);
			(*tsigs).erase((*sit).second->id);
		}
	}
	return res;
}

long_list queryImgDataForThresFast(sigMap * tsigs, double *avgl, float thresd, int sketch) {

	// will only look for average luminance
	long_list res;

	for (sigIterator sit = (*tsigs).begin(); sit != (*tsigs).end(); sit++) {
		(*sit).second->score = 0;
		for (int c = 0; c < 3; c++)
			(*sit).second->score += weights[sketch][0][c]
			                                           * fabs((*sit).second->avgl[c] - avgl[c]);
		if ((*sit).second->score < thresd) {
			res.push_back((*sit).second->id);
			(*tsigs).erase((*sit).second->id);
		}
	}
	return res;
}

//TODO some places are using double_vector others std::vector. Decide!
std::vector<double>  queryImgBlob(const int dbId, const char* data,const long length, int numres,int sketch, bool colorOnly) {
	ExceptionInfo exception;
	GetExceptionInfo(&exception);

	ImageInfo *image_info;
	image_info = CloneImageInfo((ImageInfo *) NULL);

	Image *image = BlobToImage(image_info, data, length, &exception);
	if (exception.severity != UndefinedException) CatchException(&exception);

	DestroyImageInfo(image_info);

	// Made static for speed; only used locally
	static Unit cdata1[16384];
	static Unit cdata2[16384];
	static Unit cdata3[16384];
	int i;

	Image *resize_image;

	/*
	Initialize the image info structure and read an image.
	 */
	GetExceptionInfo(&exception);

	resize_image = SampleImage(image, 128, 128, &exception);

	DestroyImage(image);

	DestroyExceptionInfo(&exception);

	if (resize_image == (Image *) NULL) {
		cerr << "ERROR: unable to resize image" << endl;
    	return vector<double>();
	}

    // store color value for basic channels
	unsigned char rchan[16384];
	unsigned char gchan[16384];
	unsigned char bchan[16384];

	GetExceptionInfo(&exception);

	const PixelPacket *pixel_cache = AcquireImagePixels(resize_image, 0, 0, 128, 128, &exception);

	for (int idx = 0; idx < 16384; idx++) {
		rchan[idx] = pixel_cache->red;
		gchan[idx] = pixel_cache->green;
		bchan[idx] = pixel_cache->blue;
		pixel_cache++;
	}

    DestroyImage(resize_image);

	transformChar(rchan, gchan, bchan, cdata1, cdata2, cdata3);

	DestroyExceptionInfo(&exception);

	SigStruct *nsig = new SigStruct();
    //TODO leaking nsig?
	calcHaar(cdata1, cdata2, cdata3,
			nsig->sig1, nsig->sig2, nsig->sig3, nsig->avgl);

	return queryImgData(dbId, nsig->sig1, nsig->sig2, nsig->sig3,
			nsig->avgl, numres, sketch, colorOnly);
}

std::vector<double> queryImgPath(const int dbId, char* path,int numres,int sketch, bool colorOnly) {

	ExceptionInfo exception;
	GetExceptionInfo(&exception);

	ImageInfo *image_info;
	image_info = CloneImageInfo((ImageInfo *) NULL);
	(void) strcpy(image_info->filename, path);
	Image *image = ReadImage(image_info, &exception);
	if (exception.severity != UndefinedException) CatchException(&exception);
	DestroyImageInfo(image_info);
	DestroyExceptionInfo(&exception);

	if (image == (Image *) NULL) {
    	cerr << "ERROR: unable to read image" << endl;
    	return vector<double>();
    }

	// Made static for speed; only used locally
	static Unit cdata1[16384];
	static Unit cdata2[16384];
	static Unit cdata3[16384];
	int i;

	Image *resize_image;

	/*
	Initialize the image info structure and read an image.
	 */
	GetExceptionInfo(&exception);

	resize_image = SampleImage(image, 128, 128, &exception);

	DestroyImage(image);

	DestroyExceptionInfo(&exception);

	if (resize_image == (Image *) NULL) {
		cerr << "ERROR: unable to resize image" << endl;
    	return vector<double>();
	}

    // store color value for basic channels
	unsigned char rchan[16384];
	unsigned char gchan[16384];
	unsigned char bchan[16384];

	GetExceptionInfo(&exception);

	const PixelPacket *pixel_cache = AcquireImagePixels(resize_image, 0, 0, 128, 128, &exception);

	for (int idx = 0; idx < 16384; idx++) {
		rchan[idx] = pixel_cache->red;
		gchan[idx] = pixel_cache->green;
		bchan[idx] = pixel_cache->blue;
		pixel_cache++;
	}

    DestroyImage(resize_image);

	transformChar(rchan, gchan, bchan, cdata1, cdata2, cdata3);

	DestroyExceptionInfo(&exception);

	SigStruct *nsig = new SigStruct();

	calcHaar(cdata1, cdata2, cdata3,
			nsig->sig1, nsig->sig2, nsig->sig3, nsig->avgl);

	return queryImgData(dbId, nsig->sig1, nsig->sig2, nsig->sig3,
			nsig->avgl, numres, sketch, colorOnly);
}


//TODO add parm for query tweaking (sketch?)
std::vector<double> queryImgID(const int dbId, long int id, int numres, int sketch, bool colorOnly) {
	/*query for images similar to the one that has this id
	numres is the maximum number of results
	 */

	if (id == -1) { // query random images
		vector<double> Vres;
		if (!validate_dbid(dbId)) { cerr << "ERROR: database space not found (" << dbId << ")" << endl; return Vres;}
		long int sz = dbSpace[dbId]->sigs.size();
		int_hashset includedIds;
		sigIterator it = dbSpace[dbId]->sigs.begin();
		for (int var = 0; var < min(sz, numres); ) { // var goes from 0 to numres
			long int rint = rand()%(sz);
			for(int pqp =0; pqp < rint; pqp++) {
				it ++;
				if (it == dbSpace[dbId]->sigs.end()) {
					it = dbSpace[dbId]->sigs.begin();
					continue;
				}
			}

			if ( includedIds.count((*it).first) == 0 ) { // havent added this random result yet
				Vres.insert(Vres.end(), (*it).first );
				Vres.insert(Vres.end(), 0 );
				includedIds.insert((*it).first);
				++var;
			}
		}
		return Vres;
	}

	if (!validate_imgid(dbId, id)) { cerr << "ERROR: image id (" << id << ") not found on given dbid (" << dbId << ") or dbid not existant" << endl ; return std::vector<double>();};

	return queryImgData(dbId, dbSpace[dbId]->sigs[id]->sig1, dbSpace[dbId]->sigs[id]->sig2, dbSpace[dbId]->sigs[id]->sig3,
			dbSpace[dbId]->sigs[id]->avgl, numres, sketch, colorOnly);
}

std::vector<double> queryImgIDFiltered(const int dbId, long int id, int numres, bloom_filter* bf, bool colorOnly) {
	/*query for images similar to the one that has this id
	numres is the maximum number of results
	 */

	if (!validate_imgid(dbId, id)) { cerr << "ERROR: image id (" << id << ") not found on given dbid (" << dbId << ") or dbid not existant" << endl ; return std::vector<double>();};
	return queryImgDataFiltered(dbId, dbSpace[dbId]->sigs[id]->sig1, dbSpace[dbId]->sigs[id]->sig2, dbSpace[dbId]->sigs[id]->sig3,
			dbSpace[dbId]->sigs[id]->avgl, numres, 0, bf, colorOnly);
}

int removeID(const int dbId, long int id) {

	if (!validate_imgid(dbId, id)) { cerr << "ERROR: image id (" << id << ") not found on given dbid (" << dbId << ") or dbid not existant" << endl ; return 0;};

	delete dbSpace[dbId]->sigs[id];
	dbSpace[dbId]->sigs.erase(id);
	// remove id from each bucket it could be in
	for (int c = 0; c < 3; c++)
		for (int pn = 0; pn < 2; pn++)
			for (int i = 0; i < 16384; i++)
				dbSpace[dbId]->imgbuckets[c][pn][i].remove(id);
	return 1;
}

double calcAvglDiff(const int dbId, long int id1, long int id2) {

	sigMap sigs = dbSpace[dbId]->sigs;

	/* return the average luminance difference */

	// are images on db ?
	if (!validate_imgid(dbId, id1)) { cerr << "ERROR: image id (" << id1 << ") not found on given dbid (" << dbId << ") or dbid not existant" << endl ; return 0;};
	if (!validate_imgid(dbId, id2)) { cerr << "ERROR: image id (" << id2 << ") not found on given dbid (" << dbId << ") or dbid not existant" << endl ; return 0;};

	return fabs(sigs[id1]->avgl[0] - sigs[id2]->avgl[0])
	+ fabs(sigs[id1]->avgl[1] - sigs[id2]->avgl[1])
	+ fabs(sigs[id1]->avgl[2] - sigs[id2]->avgl[2]);
}

double calcDiff(const int dbId, long int id1, long int id2)
{
	/* use it to tell the content-based difference between two images
	 */

	if (!validate_dbid(dbId)) { cerr << "ERROR: database space not found (" << dbId << ")" << endl; return 0;}

	if (!isImageOnDB(dbId,id1) ||
			!isImageOnDB(dbId,id2)) {
		cerr << "ERROR: image ids not found" << endl;
		return 0;
	}

	sigMap sigs = dbSpace[dbId]->sigs;

	double diff = calcAvglDiff(dbId, id1, id2);
	Idx *sig1[3] = { sigs[id1]->sig1, sigs[id1]->sig2, sigs[id1]->sig3 };
	Idx *sig2[3] = { sigs[id2]->sig1, sigs[id2]->sig2, sigs[id2]->sig3 };

	for (int b = 0; b < NUM_COEFS; b++)
		for (int c = 0; c < 3; c++)
			for (int b2 = 0; b2 < NUM_COEFS; b2++)
				if (sig2[c][b2] == sig1[c][b])
					diff -= weights[0][imgBin[abs(sig1[c][b])]][c];

	return diff;
}

int destroydb(const int dbId) {
	if (!validate_dbid(dbId)) { cerr << "ERROR: database space not found (" << dbId << ")" << endl; return 0;}
	throw string("not yet implemented");
	return 1;
}

int resetdb(const int dbId) {

	if (!validate_dbid(dbId)) { cerr << "ERROR: database space not found (" << dbId << ")" << endl; return 0;}
    // first deallocate db memory

	// deallocate all buckets

    for (int c = 0; c < 3; c++)
        for (int pn = 0; pn < 2; pn++)
            for (int i = 0; i < 16384; i++) {
                if (dbSpace[dbId])
                    dbSpace[dbId]->imgbuckets[c][pn][i].clear();
            }

    //delete sigs
    for (sigIterator it = dbSpace[dbId]->sigs.begin(); it != dbSpace[dbId]->sigs.end(); it++) {
        delete (*it).second;
    }

	//TODO must also clear other stuff, like ids filter

    dbSpace[dbId]->sigs.clear(); // this is making windows choke
    // dbSpace[dbId]->sigs = sigMap();

	//delete dbSpace[dbId];
 	//dbSpace.erase(dbId);

 	// finally the reset itself
	dbSpace[dbId] = new dbSpaceStruct();

	return 1;
}

long int getImgCount(const int dbId) {
	if (!validate_dbid(dbId)) { cerr << "ERROR: database space not found (" << dbId << ")" << endl; return 0;}
	return dbSpace[dbId]->sigs.size();
}

bloom_filter* getIdsBloomFilter(const int dbId) {
	if (!validate_dbid(dbId)) { cerr << "ERROR: database space not found (" << dbId << ")" << endl; return 0;}
	return dbSpace[dbId]->imgIdsFilter;
}

std::vector<int> getDBList() {
	vector<int> ids;
	for (dpspaceIterator it = dbSpace.begin(); it != dbSpace.end(); it++) {
		ids.push_back((*it).first);
	}
	return ids;
}

std::vector<long int> getImgIdList(const int dbId) {
	vector<long int> ids;

	// TODO is there a faster way for getting a maps key list and returning a vector from it ?
	for (sigIterator it = dbSpace[dbId]->sigs.begin(); it != dbSpace[dbId]->sigs.end(); it++) {
		ids.push_back((*it).first);
	}

	return ids;
}

bool isValidDB(const int dbId) {
	return dbSpace.count(dbId);
}

bool removedb(const int dbId) {
	if (!validate_dbid(dbId)) { cerr << "ERROR: database space not found (" << dbId << ")" << endl; return false;}

	if (resetdb(dbId)) {
		dbSpace.erase(dbId);
		return 1;
	}
	return 0;
}

// return structure containing filter with all image ids that have this keyword
keywordStruct* getKwdPostings(int hash) {
	keywordStruct* nks;
	if (!globalKwdsMap.count(hash)) { // never seen this keyword, create new postings list
		nks = new keywordStruct();
		globalKwdsMap[hash] = nks;
	} else { // already know about it just fetch then
		nks = globalKwdsMap[hash];
	}
	return nks;
}

// keywords in images
bool addKeywordImg(const int dbId, const int id, const int hash) {
	if (!validate_imgid(dbId, id)) { cerr << "ERROR: image id (" << id << ") not found on given dbid (" << dbId << ") or dbid not existant" << endl ; return false;};

	// populate keyword postings
	getKwdPostings(hash)->imgIdsFilter->insert(id);

	// populate image kwds
	return dbSpace[dbId]->sigs[id]->keywords.insert(hash).second;
}

bool addKeywordsImg(const int dbId, const int id, int_vector hashes){
	if (!validate_imgid(dbId, id)) { cerr << "ERROR: image id (" << id << ") not found on given dbid (" << dbId << ") or dbid not existant" << endl ; return false;};

	// populate keyword postings
	for (intVectorIterator it = hashes.begin(); it != hashes.end(); it++) {
		getKwdPostings(*it)->imgIdsFilter->insert(id);
	}

	// populate image kwds
	int_hashset& imgKwds = dbSpace[dbId]->sigs[id]->keywords;
	imgKwds.insert(hashes.begin(),hashes.end());
	return true;
}

bool removeKeywordImg(const int dbId, const int id, const int hash){
	if (!validate_imgid(dbId, id)) { cerr << "ERROR: image id (" << id << ") not found on given dbid (" << dbId << ") or dbid not existant" << endl ; return false;};

	//TODO remove from kwd postings, maybe creating an API method for regenerating kwdpostings filters or
	// calling it internally after a number of kwd removes
	return dbSpace[dbId]->sigs[id]->keywords.erase(hash);
}

bool removeAllKeywordImg(const int dbId, const int id){
	if (!validate_imgid(dbId, id)) { cerr << "ERROR: image id (" << id << ") not found on given dbid (" << dbId << ") or dbid not existant" << endl ; return false;};
	//TODO remove from kwd postings
	dbSpace[dbId]->sigs[id]->keywords.clear();
	return true;
}

std::vector<int> getKeywordsImg(const int dbId, const int id){
	if (!validate_imgid(dbId, id)) { cerr << "ERROR: image id (" << id << ") not found on given dbid (" << dbId << ") or dbid not existant" << endl ; return std::vector<int>();};
	int_hashset& imgKwds = dbSpace[dbId]->sigs[id]->keywords;
	int_vector ret;
	ret.insert(ret.end(),imgKwds.begin(),imgKwds.end());
	return ret;
}

std::vector<int> mostPopularKeywords(const int dbId, std::vector<long int> imgs, std::vector<int> excludedKwds, int count, int mode) {

	kwdFreqMap freqMap = kwdFreqMap();

	for (longintVectorIterator it = imgs.begin(); it != imgs.end(); it++) {
		int_hashset imgKwds = dbSpace[dbId]->sigs[*it]->keywords;

		for (int_hashset::iterator itkw = imgKwds.begin(); itkw != imgKwds.end(); itkw++) {
			if (freqMap.count(*itkw) == 0) {
				freqMap[*itkw] = 1;
			} else {
				freqMap[*itkw]++;
			}
		}
	}

	kwdFreqPriorityQueue pqKwds;

	int_hashset setExcludedKwds = int_hashset();

	for (intVectorIterator uit = excludedKwds.begin(); uit != excludedKwds.end(); uit++) {
		setExcludedKwds.insert(*uit);
	}

	for (kwdFreqMap::iterator it = freqMap.begin(); it != freqMap.end(); it++) {
		int id = it->first;
		long int freq = it->second;
		if (setExcludedKwds.count(id) > 0) continue; // skip excluded kwds
		pqKwds.push(KwdFrequencyStruct(id,freq));
	}

	int_vector res = int_vector();

	while (count >0 && !pqKwds.empty()) {
		KwdFrequencyStruct kf = pqKwds.top();
		pqKwds.pop();
		res.push_back(kf.kwdId);
		res.push_back(kf.freq);
		count--;
	}

	return res;
}

// query by keywords
std::vector<double> queryImgIDKeywords(const int dbId, long int id, int numres, int kwJoinType, int_vector keywords, bool colorOnly){
	if (!validate_dbid(dbId)) { cerr << "ERROR: database space not found (" << dbId << ")" << endl; return std::vector<double>();}

	if ((id != 0) && !validate_imgid(dbId, id)) { // not search random and image doesnt exist
		cerr << "ERROR: image id (" << id << ") not found on given dbid (" << dbId << ") or dbid not existant" << endl ;
		return std::vector<double>();
	}

	if (keywords.size() < 1) { 
		cerr << "ERROR: At least one keyword must be supplied" << endl ;
		return std::vector<double>();        
	} 

	// populate filter
	intVectorIterator it = keywords.begin();
	bloom_filter* bf = 0;

    // OR or AND each kwd postings filter to get final filter
    // start with the first one
    bf = new bloom_filter(*(getKwdPostings(*it)->imgIdsFilter));
    it++;
    for (; it != keywords.end(); it++) { // iterate the rest
        if (kwJoinType) { // and'd
            (*bf) &= *(getKwdPostings(*it)->imgIdsFilter);
        } else { // or'd
            (*bf) |= *(getKwdPostings(*it)->imgIdsFilter);
        }
    }

	if (id == 0) { // random images with these kwds

		vector<double> V; // select all images with the desired keywords
		for (sigIterator sit = dbSpace[dbId]->sigs.begin(); sit != dbSpace[dbId]->sigs.end(); sit++) {
			if (V.size() > 20*numres) break;

			if ((bf == 0) || (bf->contains((*sit).first))) { // image has desired keyword or we're querying random
				V.insert(V.end(), (*sit).first);
				V.insert(V.end(), 0);
			}
		}

		vector<double> Vres;

		for (int var = 0; var < min(V.size()/2, numres); ) { // var goes from 0 to numres
			int rint = rand()%(V.size()/2);
			if (V[rint*2] > 0) { // havent added this random result yet
				Vres.insert(Vres.end(), V[rint*2] );
				Vres.insert(Vres.end(), 0 );
				V[rint*2] = 0;
				++var;
			}
			++var;
		}

		return Vres;
	}
	return queryImgIDFiltered(dbId, id, numres, bf, colorOnly);

}

std::vector<long int> getAllImgsByKeywords(const int dbId, const int numres, int kwJoinType, std::vector<int> keywords){
	if (!validate_dbid(dbId)) { cerr << "ERROR: database space not found (" << dbId << ")" << endl; return std::vector<long int>();}

	std::vector<long int> res; // holds result of img lists

	if (keywords.size() < 1) {
		cerr << "ERROR: keywords list must have at least one hash" << endl;
		return std::vector<long int>();
	}

	// populate filter
	intVectorIterator it = keywords.begin();

	// OR or AND each kwd postings filter to get final filter
	// start with the first one
	bloom_filter* bf = new bloom_filter(*(getKwdPostings(*it)->imgIdsFilter));
	it++;
	for (; it != keywords.end(); it++) { // iterate the rest
		if (kwJoinType) { // and'd
			(*bf) &= *(getKwdPostings(*it)->imgIdsFilter);
		} else { // or'd
			(*bf) |= *(getKwdPostings(*it)->imgIdsFilter);
		}
	}

	for (sigIterator sit = dbSpace[dbId]->sigs.begin(); sit != dbSpace[dbId]->sigs.end(); sit++) {
		if (bf->contains((*sit).first)) res.push_back((*sit).first);
		if 	(res.size() >= numres) break; // ok, got enough
	}
	delete bf;
	return res;
}
double getKeywordsVisualDistance(const int dbId, int distanceType, std::vector<int> keywords){
	if (!validate_dbid(dbId)) { cerr << "ERROR: database space not found (" << dbId << ")" << endl; return 0;}

	throw string("not yet implemented");
}

// keywords
std::vector<int> getKeywordsPopular(const int dbId, const int numres) {
	if (!validate_dbid(dbId)) { cerr << "ERROR: database space not found (" << dbId << ")" << endl; return std::vector<int>();}

	throw string("not yet implemented");
}

// clustering

std::vector<clustersStruct> getClusterDb(const int dbId, const int numClusters) {
	if (!validate_dbid(dbId)) { cerr << "ERROR: database space not found (" << dbId << ")" << endl; return std::vector<clustersStruct>();}
	throw string("not yet implemented");
}
std::vector<clustersStruct> getClusterKeywords(const int dbId, const int numClusters,std::vector<int> keywords) {
	if (!validate_dbid(dbId)) { cerr << "ERROR: database space not found (" << dbId << ")" << endl; return std::vector<clustersStruct>();}
	throw string("not yet implemented");
}
