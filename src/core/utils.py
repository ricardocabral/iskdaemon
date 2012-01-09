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

import logging

log = logging.getLogger('core')

def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""
    def newFunc(*args, **kwargs):
        log.warn("Call to deprecated function %s." % func.__name__,
                      category=DeprecationWarning)
        return func(*args, **kwargs)
    newFunc.__name__ = func.__name__
    newFunc.__doc__ = func.__doc__
    newFunc.__dict__.update(func.__dict__)
    return newFunc

def dumpArgs(func):
    "This decorator dumps out the arguments passed to a function before calling it"
    argnames = func.func_code.co_varnames[:func.func_code.co_argcount]
    fname = func.func_name
    def echoFunc(*args,**kwargs):
        log.debug(fname+ "(" + ', '.join('%s=%r' % entry
                                    for entry in zip(argnames,args) + kwargs.items() if entry[0] != 'self') + ')')
        return func(*args, **kwargs)
    return echoFunc

def requireKnownDbId(func):
    "Checks if the 1st parameter (which should be a dbId is valid (has an internal dbSpace entry)"
    def checkFunc(*args,**kwargs):
        if not args[0].dbSpaces.has_key(args[1]):
            raise ImageDBException("attempt to call %s with unknown dbid %d. Have you created it first with createdb() or loaddb()?" %(func.func_name, args[1]))
        return func(*args, **kwargs)
    return checkFunc

