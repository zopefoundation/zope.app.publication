##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Tests for the HTTP Publication Request Factory.

$Id: test_publicationfactories.py 38841 2005-10-07 04:34:09Z andreasjung $
"""
from unittest import TestCase, TestSuite, main, makeSuite

from StringIO import StringIO

from zope import component, interface
from zope.interface.verify import verifyClass
from zope.component.tests.placelesssetup import PlacelessSetup

from zope.app.publication.interfaces import IRequestPublicationRegistry
from zope.app.publication.requestpublicationregistry import RequestPublicationRegistry


def DummyFactory():
    return object

class Test(PlacelessSetup, TestCase):

    def setUp(self):
        super(Test, self).setUp()
        self._registry = RequestPublicationRegistry()

    def test_interface(self):
        verifyClass(IRequestPublicationRegistry, RequestPublicationRegistry)

    def test_registration(self):
        r = self._registry
        xmlrpc_f = DummyFactory()
        r.register('POST', 'text/xml', 'xmlrpc', 0, xmlrpc_f)
        soap_f = DummyFactory()
        r.register('POST', 'text/xml', 'soap', 1, soap_f)
        browser_f = DummyFactory()
        r.register('*', '*', 'browser_default', 0, browser_f)
        l = r.getFactoriesFor('POST', 'text/xml')
        self.assertEqual(l, [{'name' : 'xmlrpc', 'priority' : 0, 'factory' : object},
                             {'name' : 'soap', 'priority' : 1, 'factory' : object},
                            ])
        self.assertEqual(r.getFactoriesFor('POST', 'text/html'), None)



def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
