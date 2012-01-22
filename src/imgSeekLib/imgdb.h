/***************************************************************************
    imgSeek ::  databse C++ module
                             -------------------
    begin                : Fri Jan 17 2003
    email                : nieder|at|mail.ru
    Time-stamp:            <2006-08-06 23:20:00 rnc>

    Copyright (C) 2003 Ricardo Niederberger Cabral

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
 ***************************************************************************
 */

#ifndef IMGDBASE_H
#define IMGDBASE_H

/* ImageMagick includes */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "haar.h"

// Weights for the Haar coefficients.
// Straight from the referenced paper:
const float weights[2][6][3]={
		// For scanned picture (sketch=0):
		//    Y      I      Q       idx total occurs
		{{ 5.00f, 19.21f, 34.37f},  // 0   58.58      1 (`DC' component)
			{ 0.83f,  1.26f,  0.36f},  // 1    2.45      3
			{ 1.01f,  0.44f,  0.45f},  // 2    1.90      5
			{ 0.52f,  0.53f,  0.14f},  // 3    1.19      7
			{ 0.47f,  0.28f,  0.18f},  // 4    0.93      9
			{ 0.30f,  0.14f,  0.27f}}, // 5    0.71      16384-25=16359

			// For handdrawn/painted sketch (sketch=1):
			//    Y      I      Q
			{{ 4.04f, 15.14f, 22.62f},
				{ 0.78f,  0.92f,  0.40f},
				{ 0.46f,  0.53f,  0.63f},
				{ 0.42f,  0.26f,  0.25f},
				{ 0.41f,  0.14f,  0.15f},
				{ 0.32f,  0.07f,  0.38f}}
};

// STL includes

#include <map>
#include <queue>
#include <list>

#ifdef LinuxBuild
    #include <ext/hash_set>
#else
    #include <hash_set>
#endif

// Global typedefs
typedef long int imageId;

/// Lists
typedef std::list<long int> long_list;
typedef long_list::iterator long_listIterator;

typedef std::list<imageId> imageId_list;
typedef imageId_list::iterator imageId_listIterator;

// Sets
#ifdef LinuxBuild
    using namespace __gnu_cxx;
    typedef __gnu_cxx::hash_set<int> int_hashset;
#else
    using namespace stdext;
    typedef stdext::hash_set<int> int_hashset;
#endif

class SigStruct;

/* persisted signature structure */
class DiskSigStruct {
public:

	imageId id;			/* picture id */
	Idx sig1[NUM_COEFS];		/* Y positions with largest magnitude */
	Idx sig2[NUM_COEFS];		/* I positions with largest magnitude */
	Idx sig3[NUM_COEFS];		/* Q positions with largest magnitude */
	double avgl[3];		/* YIQ for position [0,0] */
	/* image properties extracted when opened for the first time */
	int width;			/* in pixels */
	int height;			/* in pixels */

	DiskSigStruct() {}
	~DiskSigStruct()
	{

	}
};

/* older versions of it signature structure */
typedef struct sigStructV06_{
	imageId id;			/* picture id */
	Idx sig1[NUM_COEFS];		/* Y positions with largest magnitude */
	Idx sig2[NUM_COEFS];		/* I positions with largest magnitude */
	Idx sig3[NUM_COEFS];		/* Q positions with largest magnitude */
	double avgl[3];		/* YIQ for position [0,0] */
	double score;			/* used when doing queries */
	/* image properties extracted when opened for the first time */
	int width;			/* in pixels */
	int height;			/* in pixels */

	bool operator< (const sigStructV06_ & right) const {
		return score < (right.score);
	}
} sigStructV06;

/* in memory signature structure */
class SigStruct: public DiskSigStruct {
public:
	double score;			/* used when doing queries */
	int_hashset keywords;

	SigStruct(DiskSigStruct* ds) {
		id = ds->id;

		memcpy(sig1,ds->sig1,sizeof(sig1));
		memcpy(sig2,ds->sig2,sizeof(sig2));
		memcpy(sig3,ds->sig3,sizeof(sig3));
		memcpy(avgl,ds->avgl,sizeof(avgl));

		width=ds->width;
		height=ds->height;

	}

	SigStruct(sigStructV06* ds) {
		id = ds->id;

		memcpy(sig1,ds->sig1,sizeof(sig1));
		memcpy(sig2,ds->sig2,sizeof(sig2));
		memcpy(sig3,ds->sig3,sizeof(sig3));
		memcpy(avgl,ds->avgl,sizeof(avgl));

		width=ds->width;
		height=ds->height;

	}


	SigStruct() {
	}

	~SigStruct()
	{
	}

	bool operator< (const SigStruct & right) const {
		return score < (right.score);
	}

};

struct cmpf
{
	bool operator()(const long int s1, const long int s2) const
	{
		return s1<s2;
	}
};

// used for calculating most popular keywords
class KwdFrequencyStruct {
public:
	int kwdId;
	long int freq;	

	KwdFrequencyStruct(int kwdId, long int freq): kwdId(kwdId),freq(freq) {}

	bool operator< (const KwdFrequencyStruct & right) const {
		return freq > (right.freq);
	}
};

// typedefs
typedef std::map<const long int, SigStruct*, cmpf>::iterator sigIterator;
typedef std::priority_queue < SigStruct > sigPriorityQueue;
typedef std::priority_queue < KwdFrequencyStruct > kwdFreqPriorityQueue;
typedef long int (*long_array3)[1][1];
typedef std::map<const long int, SigStruct*, cmpf> sigMap;
typedef std::map<const int, long int> kwdFreqMap;
typedef std::vector<double> double_vector;
typedef std::vector<int> int_vector;
typedef int_vector::iterator intVectorIterator;
typedef std::vector<long int> longint_vector;
typedef longint_vector::iterator longintVectorIterator;

/* signature structure */
typedef struct srzMetaDataStruct_{
	int isValidMetadata;
	int iskVersion;
	int bindingLang;
	int isTrial;
	int compilePlat;
} srzMetaDataStruct;

/* Bloom filter globals */
#define random_bloom_seed  0

/* signature structure */
#define AVG_IMGS_PER_DBSPACE 20000 // just a guess

class dbSpaceStruct {
public:
	dbSpaceStruct() {
		imgIdsFilter = new bloom_filter(AVG_IMGS_PER_DBSPACE, 1.0/(100.0 * AVG_IMGS_PER_DBSPACE),random_bloom_seed);
	}

	~dbSpaceStruct()
	{
		delete imgIdsFilter;
	}

	sigMap sigs;

	/* Lists of picture ids, indexed by [color-channel][sign][position], i.e.,
	   R=0/G=1/B=2, pos=0/neg=1, (i*NUM_PIXELS+j)
	 */
	imageId_list imgbuckets[3][2][16384];
	bloom_filter* imgIdsFilter;
	//std::vector<long int> imgIds;	/* img list */
} ;



typedef std::map<const int, dbSpaceStruct*> dbSpaceMapType;
typedef std::map<const int, dbSpaceStruct*>::iterator  dpspaceIterator;

// Serialization constants

#define	SRZ_VERSIONED			1
#define	SRZ_V0_5_1				1
#define	SRZ_V0_6_0				2
#define	SRZ_V0_7_0				3
#define	SRZ_CUR_VERSION			3
#define	SRZ_SINGLE_DBSPACE		1
#define	SRZ_MULTIPLE_DBSPACE	2
#define	SRZ_TRIAL_VERSION		1
#define	SRZ_FULL_VERSION		2
#define	SRZ_PLAT_WINDOWS		1
#define	SRZ_PLAT_LINUX			2
#define	SRZ_LANG_PYTHON			1
#define	SRZ_LANG_JAVA			2

// Private functions
//void saveGlobalSerializationMetadata(std::ofstream& f);

// Main exported functions
double_vector queryImgID(const int dbId, long int id,int numres,int sketch, bool colorOnly);
double_vector queryImgBlob(const int dbId, const char* data,const long length, int numres,int sketch, bool colorOnly);
double_vector queryImgPath(const int dbId, char* path,int numres,int sketch, bool colorOnly);
double_vector queryImgData(const int dbId, Idx * sig1, Idx * sig2, Idx * sig3, double *avgl, int numres, int sketch, bool colorOnly);
long_list queryImgDataForThresFast(sigMap * tsigs, double *avgl, float thresd, int sketch); 

int addImage(const int dbId, const long int id, char* filename);
int savedb(const int dbId, char* filename);
int loaddb(const int dbId, char* filename);
int savealldbs(char* filename);
int loadalldbs(char* filename);
int removeID(const int dbId, long int id);
int resetdb(const int dbId);
void initDbase(const int dbId);
void closeDbase();
long int getImgCount(const int dbId);
bool isImageOnDB(const int dbId, long int id);
int getImageHeight(const int dbId, long int id);
int getImageWidth(const int dbId, long int id);
double calcAvglDiff(const int dbId, long int id1, long int id2);
double calcDiff(const int dbId, long int id1, long int id2);
double_vector getImageAvgl(const int dbId, long int id1);
int addImageBlob(const int dbId, const long int id, const char *blob, const long length);
std::vector<int> getDBList();
std::vector<long int> getImgIdList(const int dbId);
bool isValidDB(const int dbId);
int destroydb(const int dbId);
bool removedb(const int dbId);

// keywords in images
bool addKeywordImg(const int dbId, const int id, const int hash);
bool addKeywordsImg(const int dbId, const int id, std::vector<int> hashes);
bool removeKeywordImg(const int dbId, const int id, const int hash);
bool removeAllKeywordImg(const int dbId, const int id);
std::vector<int> getKeywordsImg(const int dbId, const int id);

// query by keywords
std::vector<double> queryImgIDKeywords(const int dbId, long int id, int numres, int kwJoinType, std::vector<int> keywords, bool colorOnly);
std::vector<long int> getAllImgsByKeywords(const int dbId, const int numres, int kwJoinType, std::vector<int> keywords);
double getKeywordsVisualDistance(const int dbId, int distanceType, std::vector<int> keywords);
std::vector<int> mostPopularKeywords(const int dbId, std::vector<long int> imgs, std::vector<int> excludedKwds, int count, int mode);

// keywords
std::vector<int> getKeywordsPopular(const int dbId, const int numres);

/* keyword postings structure */
#define AVG_IMGS_PER_KWD 1000

class keywordStruct {
	//std::vector<long int> imgIds;	/* img list */
public:
	keywordStruct() {
		imgIdsFilter = new bloom_filter(AVG_IMGS_PER_KWD, 1.0/(100.0 * AVG_IMGS_PER_KWD),random_bloom_seed);
	}
	bloom_filter* imgIdsFilter;

	~keywordStruct()
	{
		delete imgIdsFilter;
	}
} ;

typedef std::map<const int, keywordStruct*> keywordsMapType;
typedef std::map<const int, keywordStruct*>::iterator  keywordsMapIterator;

// clustering
/* cluster list structure */
typedef struct clustersStruct_{
	imageId id;			/* representative image id */
	std::vector<long int> imgIds;	/* img list */
	double diameter;		
} clustersStruct;

typedef std::list<clustersStruct> cluster_list;
typedef cluster_list::iterator cluster_listIterator;

std::vector<clustersStruct> getClusterDb(const int dbId, const int numClusters);
std::vector<clustersStruct> getClusterKeywords(const int dbId, const int numClusters,std::vector<int> keywords);

// summaries
bloom_filter* getIdsBloomFilter(const int dbId);

// util
keywordStruct* getKwdPostings(int hash);

#endif
