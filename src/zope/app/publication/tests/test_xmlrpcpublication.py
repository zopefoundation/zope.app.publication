##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
"""XML-RPC Publication Tests
"""
import unittest

from zope.app.publication.tests.test_zopepublication import \
     BasePublicationTests
from zope.app.publication.traversers import TestTraverser
from zope.app.publication.traversers import SimpleComponentTraverser
from zope.app.publication.xmlrpc import XMLRPCPublication
from zope.interface import Interface, implementer
from zope.proxy import removeAllProxies
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.xmlrpc import IXMLRPCView
from zope.publisher.interfaces.xmlrpc import IXMLRPCRequest
from zope.publisher.interfaces.xmlrpc import IXMLRPCPublisher
from zope.publisher.xmlrpc import TestRequest
from zope.app.publication.tests import support
from zope import component

class SimpleObject(object):
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
        class C(object):
            x = SimpleObject(1)
        ob = C()
        r = self._createRequest('/x', pub)
        component.provideAdapter(TestTraverser, (None, IXMLRPCRequest),
                                 IXMLRPCPublisher)

        ob2 = pub.traverseName(r, ob, 'x')
        self.assertEqual(removeAllProxies(ob2).v, 1)

    def testDenyDirectMethodAccess(self):
        pub = self.klass(self.db)
        class I(Interface):
            pass

        @implementer(I)
        class C(object):

            def foo(self):
                return 'bar'

        @implementer(IXMLRPCView)
        class V(object):
            def __init__(self, context, request):
                pass
            
        ob = C()
        r = self._createRequest('/foo', pub)

        component.provideAdapter(V, (I, IXMLRPCView), Interface,
                                 name='view')

        support.setDefaultViewName(I, 'view', type=IXMLRPCView)
        self.assertRaises(NotFound, pub.traverseName, r, ob, 'foo')


    def testTraverseNameView(self):
        pub = self.klass(self.db)

        class I(Interface):
            pass

        @implementer(I)
        class C(object):
            pass

        ob = C()

        @implementer(IXMLRPCView)
        class V(object):
            def __init__(self, context, request):
                pass
            

        # Register the simple traverser so we can traverse without @@
        component.provideAdapter(SimpleComponentTraverser,
                                 (Interface, IXMLRPCRequest),
                                 IXMLRPCPublisher)

        r = self._createRequest('/@@spam', pub)
        component.provideAdapter(V, (I, IXMLRPCRequest), Interface,
                                 name='spam')
        ob2 = pub.traverseName(r, ob, '@@spam')
        self.assertEqual(removeAllProxies(ob2).__class__, V)

        ob2 = pub.traverseName(r, ob, 'spam')
        self.assertEqual(removeAllProxies(ob2).__class__, V)


    def testTraverseNameSiteManager(self):
        pub = self.klass(self.db)
        class C(object):
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
