# encoding: utf-8
"""Make Twisted Deferred objects look synchronous.

Yes, I know that the premise of this module is considered heresy by the
Twisted cool-aid drinkers.  Nonetheless, it is still useful.

>>> d = functionThatReturnsDeferred()
>>> blockOn(d)
10

If the Deferred's errback is called, an exception is raised.

blockOn() also can take multiple Deferred's and will return a list of 
results:

>>> blockOn(d0, d1, d2)
['wow', 'really', 'cool']

IMPORTANT:  Before you exit the Python interpreter, you must call the
stopReactor() function.  This shuts down the Twisted reactor.

IMPORTANT:  The startReactor() function is called automatically upon
importing this module, so you don't have to.
"""
__docformat__ = "restructuredtext en"
#-------------------------------------------------------------------------------
#       Copyright (C) 2005  Fernando Perez <fperez@colorado.edu>
#                           Brian E Granger <ellisonbg@gmail.com>
#                           Benjamin Ragan-Kelley <benjaminrk@gmail.com>
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING, distributed as part of this software.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------

from twisted.internet import reactor
from twisted.python import failure
from twisted.internet import defer

from ipythonutil import gatherBoth

#-------------------------------------------------------------------------------
# Manage the reactor
#-------------------------------------------------------------------------------

def startReactor():
    """Initialize the twisted reactor, but don't start its main loop."""
    if not reactor.running:
        reactor.startRunning(installSignalHandlers=0)
    
def stopReactor():
    """Stop the twisted reactor when its main loop isn't running."""
    if reactor.running:
        reactor.callLater(0, reactor.stop)
        while reactor.running:
            reactor.iterate(TIMEOUT)

# The reactor must be stopped before Python quits or it will hang
from atexit import register
register(stopReactor)


#-------------------------------------------------------------------------------
# Implementation of the blocking mechanism
#-------------------------------------------------------------------------------

TIMEOUT = 0.05                  # Set the timeout for poll/select

class BlockingDeferred(object):
    """Wrap a Deferred into a blocking API."""
    
    def __init__(self, d):
        """Wrap a Deferred d."""
        self.d = d
        self.finished = False
        self.count = 0

    def blockOn(self):
        """Call this to block and get the result of the wrapped Deferred.
        
        On success this will return the result.
        
        On failure, it will raise an exception.
        """
        
        self.d.addBoth(self.gotResult)
        self.d.addErrback(self.gotFailure)
        
        while not self.finished:
            reactor.iterate(TIMEOUT)
            self.count += 1
        
        if isinstance(self.d.result, dict):
            f = self.d.result.get('failure', None)
            if isinstance(f, failure.Failure):
                f.raiseException()
        return self.d.result

    def gotResult(self, result):
        self.finished = True
        return result
        
    def gotFailure(self, f):
        self.finished = True
        # Now make it look like a success so the failure isn't unhandled
        return {'failure':f}
        
        
def _parseResults(result):
    if isinstance(result, (list, tuple)):
        if len(result) == 1:
            return result[0]
        else:
            return result
    else:
        return result
        
        
def blockOn(deferrable, fireOnOneCallback=0, fireOnOneErrback=0,
            consumeErrors=0):
    """Make a Deferred look synchronous.
    
    Given a Deferrable object, this will run the Twisted event look until
    the Deferred's callback and errback chains have run.  It will then 
    return the actual result or raise an exception if an error occured.
    
    >>> blockOn(functionReturningDeferred())
    10
    
    You can also pass a list of Deferreds to this function and you will
    get a list of results.
    
    >>> blockOn([d0, d1, d2])
    ['this', 'is', 'heresy']
    """
    if not isinstance(deferrable, list):
        deferrable = [deferrable]
    
    # Add a check to simply pass through plain objects.
    for i in range(len(deferrable)):
        if hasattr(deferrable[i], '__defer__'):
            deferrable[i] = deferrable[i].__defer__()
    
    d = gatherBoth(deferrable,
                   fireOnOneCallback, 
                   fireOnOneErrback,
                   consumeErrors,
                   logErrors=0)
    if not fireOnOneCallback:
        d.addCallback(_parseResults)
    bd = BlockingDeferred(d)
    return bd.blockOn()
    

# Start the reactor
startReactor()


