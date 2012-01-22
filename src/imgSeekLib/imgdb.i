%module imgdb

%include "std_vector.i"
%{
#define SWIG_FILE_WITH_INIT
#include "bloom_filter.h"
#include "imgdb.h"
%}
%include "pybuffer.i"

namespace std {
   %template(IntVector) vector<int>;
   %template(LongIntVector) vector<long int>;
   %template(DoubleVector) vector<double>;   
}

// query
%pybuffer_binary(const char *data, const long length);
std::vector<double> queryImgData(const int dbId, int * sig1, int * sig2, int * sig3, double *avgl, int numres, int sketch, bool colorOnly);
std::vector<double> queryImgID(const int dbId, long int id,int numres,int sketch, bool colorOnly);
std::vector<double> queryImgBlob(const int dbId, const char* data,const long length, int numres,int sketch, bool colorOnly);
std::vector<double> queryImgPath(const int dbId, char* path,int numres,int sketch, bool colorOnly);
long_list queryImgDataForThresFast(sigMap * tsigs, double *avgl, float thresd, int sketch); 
// add
int addImage(const int dbId, const long int id, char* filename);  //TODO should be long long int?
int addImageBlob(const int dbId, const long int id, const char *data, const long length);

// db ops
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

// image 
int getImageHeight(const int dbId, long int id);
int getImageWidth(const int dbId, long int id);
double calcAvglDiff(const int dbId, long int id1, long int id2);
double calcDiff(const int dbId, long int id1, long int id2);
std::vector<double> getImageAvgl(const int dbId, long int id1);
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
// std::vector<int> mostPopularKeywords(const int dbId, std::vector<long int> imgs, std::vector<int> excludedKwds, int count, int mode);

// keywords
std::vector<int> getKeywordsPopular(const int dbId, const int numres);

// clustering

/* cluster list structure */
typedef struct clustersStruct_{
  imageId id;   /* representative image id */
  std::vector<long int> imgIds; /* img list */
  double diameter;
} clustersStruct;

namespace std {
   %template(ClusterVector) vector<clustersStruct>;
}

std::vector<clustersStruct> getClusterDb(const int dbId, const int numClusters);
std::vector<clustersStruct> getClusterKeywords(const int dbId, const int numClusters,std::vector<int> keywords);

// summaries

bloom_filter* getIdsBloomFilter(const int dbId);

%{
#include "bloom_filter.h"
%}

class bloom_filter
{
public:
   bloom_filter(const std::size_t elem_cnt, const double prob_fp, const std::size_t rnd_sd);
   bloom_filter(const bloom_filter& filter);
   bloom_filter& operator = (const bloom_filter& filter);
  ~bloom_filter();
   void insert(const long int key);
   bool contains(const long int key);
   std::size_t size();
   bloom_filter& operator&=(const bloom_filter& filter);
   bloom_filter& operator|=(const bloom_filter& filter);
   bloom_filter& operator^=(const bloom_filter& filter);
};
