#include "bloom_filter.h"

bloom_filter& bloom_filter::operator&=(const bloom_filter& filter)
{
   /* intersection */
   if (
       (salt_count  == filter.salt_count) &&
       (table_size  == filter.table_size) &&
       (random_seed == filter.random_seed)
      )
   {
      for (std::size_t i = 0; i < (table_size / char_size); i++)
      {
         hash_table[i] &= filter.hash_table[i];
      }
   }
   return *this;
}

bloom_filter& bloom_filter::operator|=(const bloom_filter& filter)
{
   /* union */
   if (
       (salt_count  == filter.salt_count) &&
       (table_size  == filter.table_size) &&
       (random_seed == filter.random_seed)
      )
   {
      for (std::size_t i = 0; i < (table_size / char_size); i++)
      {
         hash_table[i] |= filter.hash_table[i];
      }
   }
   return *this;
}

bloom_filter& bloom_filter::operator^=(const bloom_filter& filter)
{
   /* difference */
   if (
       (salt_count  == filter.salt_count) &&
       (table_size  == filter.table_size) &&
       (random_seed == filter.random_seed)
      )
   {
      for (std::size_t i = 0; i < (table_size / char_size); i++)
      {
         hash_table[i] ^= filter.hash_table[i];
      }
   }
   return *this;
}

std::string longIntToString(long int imgId)  {
	std::stringstream oss;
	oss << imgId;	
	return oss.str();
}


void bloom_filter::generate_unique_salt()
{
   srand(static_cast<unsigned int>(random_seed));
   const std::size_t MAX_LENGTH = 5;
   while(salt.size() < salt_count)
   {
      std::string current_salt = std::string(MAX_LENGTH,0x0);
      for(std::string::iterator it = current_salt.begin(); it != current_salt.end(); ++it)
      {
         (*it) = static_cast<char>((256.0 * rand()) / RAND_MAX);
      }
      bool duplicate_found = false;
      for(std::vector<std::string>::iterator it = salt.begin(); it != salt.end(); ++it)
      {
         if (current_salt == (*it))
         {
            duplicate_found = true;
            break;
         }
      }
      if (!duplicate_found)
      {
         salt.push_back(current_salt);
      }
   }
}

bloom_filter operator & (const bloom_filter& a, const bloom_filter& b)
{
   bloom_filter result = a;
   result &= b;
   return result;
}

bloom_filter operator | (const bloom_filter& a, const bloom_filter& b)
{
   bloom_filter result = a;
   result |= b;
   return result;
}

bloom_filter operator ^ (const bloom_filter& a, const bloom_filter& b)
{
   bloom_filter result = a;
   result ^= b;
   return result;
}
