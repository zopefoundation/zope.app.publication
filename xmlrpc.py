##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id: xmlrpc.py,v 1.3 2003/01/14 20:26:05 srichter Exp $
"""
from zope.proxy.introspection import removeAllProxies
from zope.app.publication.http import ZopeHTTPPublication
from zope.component import queryView

class XMLRPCPublication(ZopeHTTPPublication):
    """XML-RPC publication handling.

       There is nothing special here right now.
    """

    def traverseName(self, request, ob, name):

        naked_ob = removeAllProxies(ob)
        view = queryView(ob, 'methods', request, self)

        if hasattr(ob, name):
            return getattr(ob, name)
        if view is not self and hasattr(view, name):
            return getattr(view, name)
        else:
            return super(XMLRPCPublication, self).traverseName(request,
                                                               ob, name)

# For now, have a factory that returns a singleton
class XMLRPCPublicationFactory:

    def __init__(self, db):
        self.__pub = XMLRPCPublication(db)

    def __call__(self):
        return self.__pub
