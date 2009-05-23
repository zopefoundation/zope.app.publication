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
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Default View Tests

$Id$
"""
from cStringIO import StringIO
from zope.component import queryMultiAdapter
from zope.component.testfiles.views import IC
from zope.configuration.xmlconfig import XMLConfig
from zope.configuration.xmlconfig import xmlconfig
from zope.interface import implements
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces import IDefaultViewName
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.testing.cleanup import cleanUp
from zope.testing.doctestunit import DocTestSuite
import unittest

template = """<configure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:browser='http://namespaces.zope.org/browser'
   i18n_domain='zope'>
   %s
   </configure>"""


class TestDefaultViewDirective(unittest.TestCase):

    def setUp(self):
        cleanUp()
        import zope.app.publication
        XMLConfig('meta.zcml', zope.app.publication)()

    def tearDown(self):
        cleanUp()

    def testDefaultView(self):
        ob = TestOb()
        request = TestRequest()
        self.assertEqual(
            queryMultiAdapter((ob, request), IDefaultViewName), None)

        xmlconfig(StringIO(template % (
            '''
            <browser:defaultView
                name="test"
                for="zope.component.testfiles.views.IC" />
            '''
            )))

        from zope.app.publication.defaultview import getDefaultViewName
        self.assertEqual(getDefaultViewName(ob, request), 'test')

    def testDefaultViewWithLayer(self):
        ob = TestOb()
        request = TestRequest()
        class FakeRequest(TestRequest):
            implements(ITestLayer)
        request2 = FakeRequest()

        self.assertEqual(
            queryMultiAdapter((ob, request2), IDefaultViewName), None)

        xmlconfig(StringIO(template % (
            '''
            <browser:defaultView
                name="test"
                for="zope.component.testfiles.views.IC" />

            <browser:defaultView
                name="test2"
                for="zope.component.testfiles.views.IC"
                layer="
                  zope.app.publication.tests.test_defaultview.ITestLayer"
                />
            '''
            )))

        from zope.app.publication.defaultview import getDefaultViewName
        self.assertEqual(getDefaultViewName(ob, request2), 'test2')
        self.assertEqual(getDefaultViewName(ob, request), 'test')

    def testDefaultViewForClass(self):
        ob = TestOb()
        request = TestRequest()
        self.assertEqual(
            queryMultiAdapter((ob, request), IDefaultViewName), None)

        xmlconfig(StringIO(template % (
            '''
            <browser:defaultView
                for="zope.app.publication.tests.test_defaultview.TestOb"
                name="test"
                />
            '''
            )))

        from zope.app.publication.defaultview import getDefaultViewName
        self.assertEqual(getDefaultViewName(ob, request), 'test')


class ITestLayer(IBrowserRequest):
    """Test Layer."""

class TestOb(object):
    implements(IC)

def cleanUpDoc(args):
    cleanUp()

def test_suite():
    return unittest.TestSuite([
        DocTestSuite('zope.app.publication.defaultview',
            setUp=cleanUpDoc, tearDown=cleanUpDoc),
        unittest.makeSuite(TestDefaultViewDirective),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
