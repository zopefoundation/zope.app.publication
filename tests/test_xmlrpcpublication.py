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
"""XML-RPC Publication Tests

$Id: test_xmlrpcpublication.py,v 1.2 2003/09/02 20:46:49 jim Exp $
"""
import unittest

from zope.app.publication.tests.test_zopepublication import \
     BasePublicationTests
from zope.app.publication.traversers import TestTraverser
from zope.app.publication.xmlrpc import XMLRPCPublication
from zope.app.services.servicenames import Views
from zope.component import getService
from zope.context import getWrapperContext
from zope.interface import Interface, implements
from zope.proxy import removeAllProxies
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.xmlrpc import IXMLRPCPresentation
from zope.publisher.xmlrpc import TestRequest


class SimpleObject:
    def __init__(self, v):
        self.v = v


class XMLRPCPublicationTests(BasePublicationTests):

    klass = XMLRPCPublication

    def _createRequest(self, path, publication, **kw):
        request = TestRequest(PATH_INFO=path, **kw)
        request.setPublication(publication)
        return request

    def testTraverseName(self):
        pub = self.klass(self.db)
        class C:
            x = SimpleObject(1)
        ob = C()
        r = self._createRequest('/x', pub)
        provideView=getService(None, Views).provideView
        provideView(None, '_traverse', IXMLRPCPresentation, [TestTraverser])
        ob2 = pub.traverseName(r, ob, 'x')
        self.assertEqual(removeAllProxies(ob2).v, 1)
        self.assertEqual(getWrapperContext(ob2), ob)

    def testDenyDirectMethodAccess(self):
        pub = self.klass(self.db)
        class I(Interface):
            pass

        class C:
            implements(I)

            def foo(self):
                return 'bar'

        class V:
            def __init__(self, context, request):
                pass
            implements(IXMLRPCPresentation)

        ob = C()
        r = self._createRequest('/foo', pub)
        provideView=getService(None, Views).provideView
        setDefaultViewName=getService(None, Views).setDefaultViewName
        provideView(I, 'view', IXMLRPCPresentation, [V])
        setDefaultViewName(I, IXMLRPCPresentation, 'view')
        self.assertRaises(NotFound, pub.traverseName, r, ob, 'foo')


    def testTraverseNameView(self):
        pub = self.klass(self.db)

        class I(Interface):
            pass

        class C:
            implements(I)

        ob = C()

        class V:
            def __init__(self, context, request):
                pass
            implements(IXMLRPCPresentation)

        r = self._createRequest('/@@spam', pub)
        provideView=getService(None, Views).provideView
        provideView(I, 'spam', IXMLRPCPresentation, [V])
        ob2 = pub.traverseName(r, ob, '@@spam')
        self.assertEqual(removeAllProxies(ob2).__class__, V)
        self.assertEqual(getWrapperContext(ob2), ob)

        ob2 = pub.traverseName(r, ob, 'spam')
        self.assertEqual(removeAllProxies(ob2).__class__, V)
        self.assertEqual(getWrapperContext(ob2), ob)


    def testTraverseNameDefaultView(self):
        pub = self.klass(self.db)

        class I(Interface):
            pass

        class C:
            implements(I)

        ob = C()

        class V:
            implements(IXMLRPCPresentation)

            def __init__(self, context, request):
                pass

            def spam(self):
                return 'foo'

        r = self._createRequest('/spam', pub)
        provideView=getService(None, Views).provideView
        setDefaultViewName=getService(None, Views).setDefaultViewName
        provideView(I, 'view', IXMLRPCPresentation, [V])
        setDefaultViewName(I, IXMLRPCPresentation, 'view')

        ob2 = pub.traverseName(r, ob, '@@spam')
        self.assertEqual(removeAllProxies(ob2).__name__, V.spam.__name__)
        self.assertEqual(getWrapperContext(ob2), ob)

        ob2 = pub.traverseName(r, ob, 'spam')
        self.assertEqual(removeAllProxies(ob2).__name__, V.spam.__name__)
        self.assertEqual(getWrapperContext(ob2), ob)


    def testTraverseNameServices(self):
        pub = self.klass(self.db)
        class C:
            def getSiteManager(self):
                return SimpleObject(1)
        ob = C()
        r = self._createRequest('/++etc++site',pub)
        ob2 = pub.traverseName(r, ob, '++etc++site')
        self.assertEqual(removeAllProxies(ob2).v, 1)
        self.assertEqual(getWrapperContext(ob2), ob)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(XMLRPCPublicationTests),
        ))

if __name__ == '__main__':
    unittest.main()
