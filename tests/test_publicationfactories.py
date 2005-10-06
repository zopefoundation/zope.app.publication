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

$Id$
"""
from unittest import TestCase, TestSuite, main, makeSuite

from StringIO import StringIO

from zope import component, interface
from zope.publisher.browser import BrowserRequest
from zope.publisher.http import HTTPRequest
from zope.publisher.xmlrpc import XMLRPCRequest
from zope.component.tests.placelesssetup import PlacelessSetup

from zope.app.publication.httpfactory import HTTPPublicationRequestFactory
from zope.app.publication.browser import BrowserPublication
from zope.app.publication.http import HTTPPublication
from zope.app.publication.xmlrpc import XMLRPCPublication
from zope.app.testing import ztapi
from zope.app.publication import interfaces
from zope.app.publication.publicationfactories import SOAPFactory 
from zope.app.publication.soap import SOAPPublication

class DummyRequestFactory(object):
    def __call__(self, input_stream, env):
        self.input_stream = input_stream
        self.env = env
        return self

    def setPublication(self, pub):
        self.pub = pub
 

class Test(PlacelessSetup, TestCase):

    def setUp(self):
        super(Test, self).setUp()
        self.__env =  {
            'SERVER_URL':         'http://127.0.0.1',
            'HTTP_HOST':          '127.0.0.1',
            'CONTENT_LENGTH':     '0',
            'GATEWAY_INTERFACE':  'TestFooInterface/1.0',
            }

    def test_soapfactory(self):
        soaprequestfactory = DummyRequestFactory()
        interface.directlyProvides(
            soaprequestfactory, interfaces.ISOAPRequestFactory)
        component.provideUtility(soaprequestfactory)
        env = self.__env
        env['HTTP_SOAPACTION'] = 'server:foo'
        factory = SOAPFactory()
        self.assertEqual(factory.canHandle(env), True)
        request, publication = factory.getRequestPublication()
        self.assertEqual(isinstance(request, DummyRequestFactory), True)
        self.assertEqual(publication, SOAPPublication)

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
