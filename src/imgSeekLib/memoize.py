# -*- coding: iso-8859-1 -*-
###############################################################################
# begin                : Sun Aug  6, 2006  4:58 PM
# copyright            : (C) 2003 by Ricardo Niederberger Cabral
# email                : ricardo dot cabral at imgseek dot net
#
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

"""from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/498110
"""

import logging

log = logging.getLogger('ImageDB')

import cPickle

__all__ = ['memoize']

# This would usually be defined elsewhere
class decoratorargs(object):
	def __new__(typ, *attr_args, **attr_kwargs):
		def decorator(orig_func):
			self = object.__new__(typ)
			self.__init__(orig_func, *attr_args, **attr_kwargs)
			return self
		
		return decorator


class memoize(decoratorargs):
	class Node:
		__slots__ = ['key', 'value', 'older', 'newer']
		def __init__(self, key, value, older=None, newer=None):
			self.key = key
			self.value = value
			self.older = older
			self.newer = newer
	
	def __init__(self, func, capacity, keyfunc=lambda *args, **kwargs: cPickle.dumps((args, kwargs))):
		self.func = func
		self.capacity = capacity
		self.keyfunc = keyfunc
		self.reset()
	
	def reset(self):
		self.mru = self.Node(None, None)
		self.mru.older = self.mru.newer = self.mru
		self.nodes = {self.mru.key: self.mru}
		self.count = 1
		self.hits = 0
		self.misses = 0
	
	def __call__(self, *args, **kwargs):
		key = self.keyfunc(*args, **kwargs)
		try:
			node = self.nodes[key]
			log.debug("internal cache hit for '%s'"%key)
		except KeyError:
			log.debug("internal cache miss for '%s'"%key)
			# We have an entry not in the cache
			self.misses += 1
			
			value = self.func(*args, **kwargs)

			lru = self.mru.newer  # Always true
			
			# If we haven't reached capacity
			if self.count < self.capacity:
				# Put it between the MRU and LRU - it'll be the new MRU
				node = self.Node(key, value, self.mru, lru)
				self.mru.newer = node
	
				lru.older = node
				self.mru = node
				self.count += 1
			else:
				# It's FULL! We'll make the LRU be the new MRU, but replace its
				# value first
				del self.nodes[lru.key]  # This mapping is now invalid
				lru.key = key
				lru.value = value
				self.mru = lru

			# Add the new mapping
			self.nodes[key] = self.mru
			return value
		
		# We have an entry in the cache
		self.hits += 1
		
		# If it's already the MRU, do nothing
		if node is self.mru:
			return node.value
		
		lru = self.mru.newer  # Always true
		
		# If it's the LRU, update the MRU to be it
		if node is lru:
			self.mru = lru
			return node.value
		
		# Remove the node from the list
		node.older.newer = node.newer
		node.newer.older = node.older
		
		# Put it between MRU and LRU
		node.older = self.mru
		self.mru.newer = node
		
		node.newer = lru
		lru.older = node
		
		self.mru = node
		return node.value

class simple_memoized(object):
   """Decorator that caches a function's return value each time it is called.
   If called later with the same arguments, the cached value is returned, and
   not re-evaluated.
   """
   def __init__(self, func):
      self.func = func
      self.cache = {}
   def __call__(self, *args):
      try:
         return self.cache[args]
      except KeyError:
      	 log.debug("internal cache miss for '%s'"%args)
         self.cache[args] = value = self.func(*args)
         return value
      except TypeError:
         # uncachable -- for instance, passing a list as an argument.
         # Better to not cache than to blow up entirely.
         return self.func(*args)
   def __repr__(self):
      """Return the function's docstring."""
      return self.func.__doc__

   def __name__(self):
      """Return the function's docstring."""
      return "asda"
      return self.func.__name__+"_memoized"

"""

# Example usage - fib only needs a cache size of 3 to keep it from
# being an exponential-time algorithm
@memoize(3)
def fib(n): return (n > 1) and (fib(n - 1) + fib(n - 2)) or 1

fib(100)  # => 573147844013817084101L

# This is faster because it doesn't use the default key function -
# it doesn't need to call cPickle.dumps((*args, **kwargs))
@memoize(100, lambda n: n)
def fib(n): return (n > 1) and (fib(n - 1) + fib(n - 2)) or 1

fib(100)  # => 573147844013817084101L

# See what's in the cache
# => [(98, 218922995834555169026L), (99, 354224848179261915075L), (100, 573147844013817084101L)]
[(node.key, node.value) for node in fib.nodes.values()]

# Get an example of the key function working
fib.keyfunc(40)  # => 40

# Simple report on performance
# => Hit %: 0.492462
print 'Hit %%: %f' % (float(fib.hits) / (fib.hits + fib.misses))

# Resize the LRU cache
fib.capacity = 100
fib.reset()  # Not necessary unless you shrink it

"""