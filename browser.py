##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""XXX short summary goes here.

$Id: browser.py,v 1.6 2003/02/11 15:59:52 sidnei Exp $
"""
__metaclass__ = type

from zope.app.publication.publicationtraverse \
     import PublicationTraverser as PublicationTraverser_
from zope.app.publication.zopepublication import ZopePublication
from zope.component import queryAdapter, queryView
from zope.proxy.context import ContextWrapper
from zope.proxy.introspection import removeAllProxies
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.security.checker import ProxyFactory

class PublicationTraverser(PublicationTraverser_):

    def traverseRelativeURL(self, request, ob, path):

        ob = self.traversePath(request, ob, path)

        while 1:
            adapter = queryAdapter(ob, IBrowserPublisher)
            if adapter is None:
                return ob
            ob, path = adapter.browserDefault(request)
            ob = ProxyFactory(ob)
            if not path:
                return ob

            ob = self.traversePath(request, ob, path)

class BrowserPublication(ZopePublication):
    """Web browser publication handling."""

    def getDefaultTraversal(self, request, ob):

        r = ()

        if IBrowserPublisher.isImplementedBy(removeAllProxies(ob)):
            r = ob.browserDefault(request)
        else:
            adapter = queryView(ob, '_traverse', request , None)
            if adapter is not None:
                r = adapter.browserDefault(request)
            else:
                return (ob, None)

        if r[0] is ob:
            return r

        wrapped = ContextWrapper(ProxyFactory(r[0]), ob, name=None)
        return (wrapped, r[1])

    def afterCall(self, request):
        super(BrowserPublication, self).afterCall(request)
        if request.method == 'HEAD':
            request.response.setBody('')

# For now, have a factory that returns a singleton
class PublicationFactory:

    def __init__(self, db):
        self.__pub = BrowserPublication(db)

    def __call__(self):
        return self.__pub
