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

def tail( f, window=20 ):
    "returns last n ines from text file"
    # http://stackoverflow.com/questions/136168/get-last-n-lines-of-a-file-with-python-similar-to-tail
    BUFSIZ = 1024
    f.seek(0, 2)
    bytes = f.tell()
    size = window
    block = -1
    data = []
    while size > 0 and bytes > 0:
        if (bytes - BUFSIZ > 0):
            # Seek back one whole BUFSIZ
            f.seek(block*BUFSIZ, 2)
            # read BUFFER
            data.append(f.read(BUFSIZ))
        else:
            # file too small, start from begining
            f.seek(0,0)
            # only read what was not read
            data.append(f.read(bytes))
        linesFound = data[-1].count('\n')
        size -= linesFound
        bytes -= BUFSIZ
        block -= 1
    return '\n'.join(''.join(data).splitlines()[-window:])
