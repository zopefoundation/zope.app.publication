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

$Id: xmlrpc.py,v 1.2 2002/12/25 14:13:08 jim Exp $
"""

from zope.proxy.introspection import removeAllProxies
from zope.app.publication.http import ZopeHTTPPublication

class XMLRPCPublication(ZopeHTTPPublication):
    """XML-RPC publication handling.

       There is nothing special here right now.
    """

    def traverseName(self, request, ob, name):

        naked_ob = removeAllProxies(ob)
        if hasattr(ob, name):
            return getattr(ob, name)
        else:
            return super(XMLRPCPublication, self).traverseName(request,
                                                               ob, name)


# For now, have a factory that returns a singleton
class XMLRPCPublicationFactory:

    def __init__(self, db):
        self.__pub = XMLRPCPublication(db)

    def __call__(self):
        return self.__pub
