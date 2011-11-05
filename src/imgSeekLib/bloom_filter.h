/*
 **************************************************************************
 *                                                                        *
 *                           Open Bloom Filter                            *
 *                                                                        *
 * Author: Arash Partow - 2000                                            *
 * URL: http://www.partow.net                                             *
 * URL: http://www.partow.net/programming/hashfunctions/index.html        *
 *                                                                        *
 * Copyright notice:                                                      *
 * Free use of the Bloom Filter Library is permitted under the guidelines *
 * and in accordance with the most current version of the Common Public   *
 * License.                                                               *
 * http://www.opensource.org/licenses/cpl.php                             *
 *                                                                        *
 **************************************************************************
*/


#ifndef INCLUDE_BLOOM_FILTER_H
#define INCLUDE_BLOOM_FILTER_H

#include <string>
#include <vector>
#include <algorithm>
#include <cmath>
#include <limits>
#include <sstream>

#include <stdlib.h>


const std::size_t   char_size   = 0x08;    // 8 bits in 1 char(unsigned)
const unsigned char bit_mask[char_size] = {
                                           0x01,  //00000001
                                           0x02,  //00000010
                                           0x04,  //00000100
                                           0x08,  //00001000
                                           0x10,  //00010000
                                           0x20,  //00100000
                                           0x40,  //01000000
                                           0x80   //10000000
                                          };

std::string longIntToString(long int imgId);

class bloom_filter
{
public:

   bloom_filter(const std::size_t elem_cnt, const double prob_fp, const std::size_t rnd_sd) : hash_table(0),
                                                                                              element_count(elem_cnt),
                                                                                              random_seed(rnd_sd),
                                                                                              prob_false_positive(prob_fp)
   {
      find_optimal_parameters();
      hash_table = new unsigned char[table_size / char_size];
      generate_unique_salt();
      for (std::size_t i = 0; i < (table_size / char_size); i++)
      {
         hash_table[i] = static_cast<unsigned char>(0x0);
      }
   }

   bloom_filter(const bloom_filter& filter)
   {
      salt_count          = filter.salt_count;
      table_size          = filter.table_size;
      element_count       = filter.element_count;
      random_seed         = filter.random_seed;
      prob_false_positive = filter.prob_false_positive;
      hash_table = new unsigned char[table_size / char_size];
      for (std::size_t i = 0; i < (table_size / char_size); i++)
      {
         hash_table[i] = filter.hash_table[i];
      }
      salt.clear();
      std::copy(filter.salt.begin(),filter.salt.end(),std::back_inserter(salt));
   }


   bloom_filter& operator = (const bloom_filter& filter)
   {
      salt_count          = filter.salt_count;
      table_size          = filter.table_size;
      element_count       = filter.element_count;
      random_seed         = filter.random_seed;
      prob_false_positive = filter.prob_false_positive;
      delete[] hash_table;
      hash_table = new unsigned char[table_size / char_size];
      for (std::size_t i = 0; i < (table_size / char_size); i++)
      {
         hash_table[i] = filter.hash_table[i];
      }
      salt.clear();
      std::copy(filter.salt.begin(),filter.salt.end(),std::back_inserter(salt));
      return *this;
   }

  ~bloom_filter()
   {
      delete[] hash_table;
   }

   void insert(const long int nid)
   {
	   std::string key = longIntToString (nid);

      for(std::vector<std::string>::iterator it = salt.begin(); it != salt.end(); ++it)
      {
         std::size_t bit_index = hash_ap(key + (*it)) % table_size;
         hash_table[bit_index / char_size] |= bit_mask[bit_index % char_size];
      }
   }

   bool contains(const long int nid)
   {
	   std::string key = longIntToString (nid);

      for(std::vector<std::string>::iterator it = salt.begin(); it != salt.end(); ++it)
      {
         std::size_t bit_index = hash_ap(key + (*it)) % table_size;
         std::size_t bit       = bit_index % char_size;
         if ((hash_table[bit_index / char_size] & bit_mask[bit]) != bit_mask[bit])
         {
            return false;
         }
      }
      return true;
   }

   std::size_t size() { return table_size; }

   bloom_filter& operator&=(const bloom_filter& filter);
   bloom_filter& operator|=(const bloom_filter& filter);
   bloom_filter& operator^=(const bloom_filter& filter);

private:

   void generate_unique_salt();

   std::size_t hash_ap(const std::string& str)
   {
      /* Arash Partow Hash Function */
      std::size_t hash = 0;
      for(std::size_t i = 0; i < str.length(); i++)
      {
         hash ^= ((i & 1) == 0) ? (  (hash <<  7) ^ str[i] ^ (hash >> 3)) :
                                  (~((hash << 11) ^ str[i] ^ (hash >> 5)));
      }
      return hash;
   }

   void find_optimal_parameters()
   {
      double min_m  = std::numeric_limits<double>::infinity();
      double min_k  = 0.0;
      double curr_m = 0.0;
      for(double k = 0; k < 1000.0; k++)
      {
         if ((curr_m = ((- k * element_count) / std::log(1 - std::pow(prob_false_positive,1 / k)))) < min_m)
         {
            min_m = curr_m;
            min_k = k;
         }
      }
      salt_count = static_cast<std::size_t>(min_k);
      table_size = static_cast<std::size_t>(min_m);
      table_size += (((table_size % char_size) != 0) ? (char_size - (table_size % char_size)) : 0);
   }

   std::vector<std::string> salt;
   unsigned char*           hash_table;
   std::size_t              salt_count;
   std::size_t              table_size;
   std::size_t              element_count;
   std::size_t              random_seed;
   double                   prob_false_positive;
};

bloom_filter operator & (const bloom_filter& a, const bloom_filter& b);
bloom_filter operator | (const bloom_filter& a, const bloom_filter& b);
bloom_filter operator ^ (const bloom_filter& a, const bloom_filter& b);


#endif
