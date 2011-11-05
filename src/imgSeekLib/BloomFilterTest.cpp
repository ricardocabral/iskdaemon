/*
 **************************************************************************
 *                                                                        *
 *                        Open Bloom Filter Test                          *
 *                                                                        *
 * Author: Arash Partow - 2000                                            *
 * URL: http://www.partow.net                                             *
 * URL: http://www.partow.net/programming/hashfunctions/index.html        *
 *                                                                        *
 * Copyright notice:                                                      *
 * Free use of the General Purpose Hash Function Algorithms Library is    *
 * permitted under the guidelines and in accordance with the most current *
 * version of the Common Public License.                                  *
 * http://www.opensource.org/licenses/cpl.php                             *
 *                                                                        *
 **************************************************************************
*/

#include <iostream>
#include <fstream>
#include <iterator>
#include <algorithm>
#include <vector>
#include <string>

#include "bloom_filter.h"


void read_file(const std::string file_name, std::vector<std::string>& buffer);
std::string reverse(std::string str);

void generate_outliers(std::vector<std::string> word_list, std::vector<std::string>& outliers);

int main(int argc, char* argv[])
{

   std::vector<std::string> word_list;
   std::vector<std::string> outliers;

   read_file("word-list-large.txt",word_list);

   if (word_list.empty())
   {
      std::cout << "ERROR: Input file invalid!" << std::endl;
      return false;
   }

   generate_outliers(word_list,outliers);

   unsigned int random_seed          = 0;
   double       total_false_positive = 0.0;
   while(random_seed < 1000)
   {
      bloom_filter  filter(word_list.size(),1.0/(100.0 * word_list.size()),random_seed++);

      for(std::vector<std::string>::iterator it = word_list.begin(); it != word_list.end(); ++it)
      {
         filter.insert(*it);
      }

      for(std::vector<std::string>::iterator it = word_list.begin(); it != word_list.end(); ++it)
      {
         if (!filter.contains(*it))
         {
            std::cout << "ERROR: key not found! =>" << (*it) << std::endl;
         }
      }

      for(std::vector<std::string>::iterator it = outliers.begin(); it != outliers.end(); ++it)
      {
         if (filter.contains(*it))
         {
            //std::cout << "ERROR: key that does not exist found! => " << (*it) << std::endl;
            total_false_positive++;
         }
      }
      std::cout << "Round: " << random_seed <<
                   "\tTotal queries: " << (random_seed + 1) * (outliers.size() + word_list.size()) <<
                   "\tFalse queries: " << total_false_positive <<
                   "\tIPFP:" << 1.0/(10.0 * word_list.size()) <<
                   "\tPFP:" << total_false_positive / ((random_seed + 1) * (outliers.size() + word_list.size())) <<
                   "\tDPFP:" << (total_false_positive / ((random_seed + 1) * (outliers.size() + word_list.size()))) - (1.0/(10.0 * word_list.size())) << std::endl;

   }

   return true;
}


void read_file(const std::string file_name, std::vector<std::string>& buffer)
{
   /* Assumes no whitespace in the lines being read in. */
   std::ifstream in_file(file_name.c_str());
   if (!in_file)
   {
      return;
   }

   std::istream_iterator< std::string > is(in_file);
   std::istream_iterator< std::string > eof;
   std::copy( is, eof, std::back_inserter(buffer));
}

std::string reverse(std::string str)
{
   char tempch;

   /* Reverse the string */
   for(unsigned int i = 0; i < (str.length() / 2); i++)
   {
      tempch = str[i];
      str[i] = str[str.length() - i - 1];
      str[str.length() - i - 1] = tempch;
   }

   return str;
}

void generate_outliers(std::vector<std::string> word_list, std::vector<std::string>& outliers)
{
   for(std::vector<std::string>::iterator it = word_list.begin(); it != word_list.end(); ++it)
   {
      if ((*it) != reverse((*it)))
      {
         outliers.push_back((*it) + reverse((*it)));
         outliers.push_back((*it) + (*it));
         outliers.push_back(reverse((*it)) + (*it) + reverse((*it)));
      }
   }
}

