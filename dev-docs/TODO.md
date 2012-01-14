Promote
========

memcached
=========
isk-damon (top):

### Memcached client
def initRemoteCache():
    from imgSeekLib import memcache
    return memcache.Client(settings.memcachedHosts, debug=settings.memcachedDebug)

    """
    mc.set("some_key", "Some value")
    value = mc.get("some_key")

    mc.set("another_key", 3)
    mc.delete("another_key")
    
    mc.set("key", "1")   # note that the key used for incr/decr must be a string.
    """    

class MemcachedMemoized(object):
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
         self.cache[args] = value = self.func(*args)
         return value
      except TypeError:
         # uncachable -- for instance, passing a list as an argument.
         # Better to not cache than to blow up entirely.
         return self.func(*args)
   def __repr__(self):
      """Return the function's docstring."""
      return self.func.__doc__



__main__:

    fixSettings()

    global remoteCache
    if settings.useMemcached:
        remoteCache = initRemoteCache()



settings.py

###### internal cache settings
useInternalCache = True                       # True = enabled, False = disabled
internalCacheSize = 3                     # comma separated list of 'host:port' pairs, one for each memcached server

###### memcached settings
useMemcached = False                       # True = enabled, False = disabled
memcachedHosts = ['127.0.0.1:11211']       # comma separated list of 'host:port' pairs, one for each memcached server
memcachedDebug = 1                         # 1 = print memcached debug messages, 0 otherwise

