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

$Id: test_xmlrpcpublication.py,v 1.8 2004/03/19 20:26:30 srichter Exp $
"""
import unittest

from zope.app.publication.tests.test_zopepublication import \
     BasePublicationTests
from zope.app.publication.traversers import TestTraverser
from zope.app.publication.xmlrpc import XMLRPCPublication
from zope.app.servicenames import Presentation
from zope.component import getService
from zope.interface import Interface, implements
from zope.proxy import removeAllProxies
from zope.publisher.interfaces import NotFound
from zope.app.publisher.interfaces.xmlrpc import IXMLRPCPresentation
from zope.publisher.interfaces.xmlrpc import IXMLRPCRequest
from zope.publisher.interfaces.xmlrpc import IXMLRPCPublisher
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
        provideView = getService(None, Presentation).provideView
        provideView(None, '', IXMLRPCRequest, TestTraverser,
                    providing=IXMLRPCPublisher)
        ob2 = pub.traverseName(r, ob, 'x')
        self.assertEqual(removeAllProxies(ob2).v, 1)

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
        provideView=getService(None, Presentation).provideView
        setDefaultViewName=getService(None, Presentation).setDefaultViewName
        provideView(I, 'view', IXMLRPCPresentation, V)
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
        provideView=getService(None, Presentation).provideView
        provideView(I, 'spam', IXMLRPCRequest, V)
        ob2 = pub.traverseName(r, ob, '@@spam')
        self.assertEqual(removeAllProxies(ob2).__class__, V)
        
        ob2 = pub.traverseName(r, ob, 'spam')
        self.assertEqual(removeAllProxies(ob2).__class__, V)
        

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
        provideView=getService(None, Presentation).provideView
        setDefaultViewName=getService(None, Presentation).setDefaultViewName
        provideView(I, 'view', IXMLRPCRequest, V)
        setDefaultViewName(I, IXMLRPCRequest, 'view')

        ob2 = pub.traverseName(r, ob, '@@spam')
        self.assertEqual(removeAllProxies(ob2).__name__, V.spam.__name__)

        ob2 = pub.traverseName(r, ob, 'spam')
        self.assertEqual(removeAllProxies(ob2).__name__, V.spam.__name__)


    def testTraverseNameServices(self):
        pub = self.klass(self.db)
        class C:
            def getSiteManager(self):
                return SimpleObject(1)
        ob = C()
        r = self._createRequest('/++etc++site',pub)
        ob2 = pub.traverseName(r, ob, '++etc++site')
        self.assertEqual(removeAllProxies(ob2).v, 1)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(XMLRPCPublicationTests),
        ))

if __name__ == '__main__':
    unittest.main()
