##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""A registry for Request-Publication factories.


$Id: publicationfactories.py 38841 2005-10-07 04:34:09Z andreasjung $
"""
__docformat__ = 'restructuredtext'

from zope.interface import implements
from zope.app.publication.interfaces import IRequestPublicationRegistry

class RequestPublicationRegistry(object):

    implements(IRequestPublicationRegistry)

    def __init__(self):
        self._d = {}   # method -> { mimetype -> [factories]}

    def register(self, method, mimetype, name, priority, factory):
        """ registers a factory for method+mimetype """

        if not self._d.has_key(method):
            self._d[method] = {}
        if not self._d[method].has_key(mimetype):
            self._d[method][mimetype] = []
        l = self._d[method][mimetype]
        for pos, d in enumerate(l): # override existing factory by name
            if d['name'] == name:
                del l[pos]
                break
        l.append({'name' : name, 'factory' : factory, 'priority' : priority})
        l.sort(lambda x,y: cmp(x['priority'], y['priority']))

    def getFactoriesFor(self, method, mimetype):
        try:
            return self._d[method][mimetype]
        except:
            return None
        

    def lookup(self, method, mimetype, environment):
        """ Lookup a factory for a given method+mimetype and a 
            enviroment. 
        """



