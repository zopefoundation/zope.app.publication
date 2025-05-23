##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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
"""
from io import BytesIO
from unittest import TestCase

from zope.component.testing import PlacelessSetup
from zope.publisher.browser import BrowserRequest
from zope.publisher.http import HTTPRequest
from zope.publisher.xmlrpc import XMLRPCRequest

from zope import component
from zope import interface
from zope.app.publication import interfaces
from zope.app.publication.browser import BrowserPublication
from zope.app.publication.http import HTTPPublication
from zope.app.publication.httpfactory import HTTPPublicationRequestFactory
from zope.app.publication.requestpublicationfactories import BrowserFactory
from zope.app.publication.requestpublicationfactories import HTTPFactory
from zope.app.publication.requestpublicationfactories import SOAPFactory
from zope.app.publication.requestpublicationfactories import XMLRPCFactory
from zope.app.publication.requestpublicationregistry import factoryRegistry
from zope.app.publication.xmlrpc import XMLRPCPublication


class DummyRequestFactory:
    def __call__(self, input_stream, env):
        self.input_stream = input_stream
        self.env = env
        return self

    def setPublication(self, pub):
        self.pub = pub


class Test(PlacelessSetup, TestCase):

    def setUp(self):
        super().setUp()
        self.__factory = HTTPPublicationRequestFactory(None)
        self.__env = {
            'SERVER_URL': 'http://127.0.0.1',
            'HTTP_HOST': '127.0.0.1',
            'CONTENT_LENGTH': '0',
            'GATEWAY_INTERFACE': 'TestFooInterface/1.0',
        }

        # Simulate standard configuration
        factoryRegistry.register('GET', '*', 'browser', 0, BrowserFactory())
        factoryRegistry.register('POST', '*', 'browser', 0, BrowserFactory())
        factoryRegistry.register('HEAD', '*', 'browser', 0, BrowserFactory())
        factoryRegistry.register('*', '*', 'http', 0, HTTPFactory())
        factoryRegistry.register('POST', 'text/xml', 'xmlrpc', 20,
                                 XMLRPCFactory())
        factoryRegistry.register('POST', 'text/xml', 'soap', 30,
                                 SOAPFactory())

    def test_override(self):
        # TODO: making a SOAP request without configuring a SOAP request
        # currently generates an XMLRPC request.  Not sure what the right thing
        # is, but that doesn't seem to be the right thing.
        soaprequestfactory = DummyRequestFactory()
        interface.directlyProvides(
            soaprequestfactory, interfaces.ISOAPRequestFactory)
        component.provideUtility(soaprequestfactory)
        xmlrpcrequestfactory = DummyRequestFactory()
        interface.directlyProvides(
            xmlrpcrequestfactory, interfaces.IXMLRPCRequestFactory)
        component.provideUtility(xmlrpcrequestfactory)
        httprequestfactory = DummyRequestFactory()
        interface.directlyProvides(
            httprequestfactory, interfaces.IHTTPRequestFactory)
        component.provideUtility(httprequestfactory)
        browserrequestfactory = DummyRequestFactory()
        interface.directlyProvides(
            browserrequestfactory, interfaces.IBrowserRequestFactory)
        component.provideUtility(browserrequestfactory)
        httpfactory = HTTPPublicationRequestFactory(None)
        env = self.__env
        env['REQUEST_METHOD'] = 'POST'
        env['CONTENT_TYPE'] = 'text/xml'
        input = BytesIO(b'')
        env['HTTP_SOAPACTION'] = 'foo'
        self.assertEqual(httpfactory(input, env), soaprequestfactory)
        del env['HTTP_SOAPACTION']
        self.assertEqual(httpfactory(input, env), xmlrpcrequestfactory)
        env['CONTENT_TYPE'] = 'text/foo'
        self.assertEqual(
            httpfactory(input, env), browserrequestfactory)
        env['REQUEST_METHOD'] = 'FLOO'
        self.assertEqual(httpfactory(input, env), httprequestfactory)

    def test_browser(self):
        r = self.__factory(BytesIO(b''), self.__env)
        self.assertEqual(r.__class__, BrowserRequest)
        self.assertEqual(r.publication.__class__, BrowserPublication)

        for method in ('GET', 'HEAD', 'POST', 'get', 'head', 'post'):
            self.__env['REQUEST_METHOD'] = method
            r = self.__factory(BytesIO(b''), self.__env)
            self.assertEqual(r.__class__, BrowserRequest)
            self.assertEqual(r.publication.__class__, BrowserPublication)

    def test_http(self):
        for method in ('PUT', 'put', 'ZZZ'):
            self.__env['REQUEST_METHOD'] = method
            r = self.__factory(BytesIO(b''), self.__env)
            self.assertEqual(r.__class__, HTTPRequest)
            self.assertEqual(r.publication.__class__, HTTPPublication)

    def test_xmlrpc(self):
        self.__env['CONTENT_TYPE'] = 'text/xml'
        for method in ('POST', 'post'):
            self.__env['REQUEST_METHOD'] = method
            r = self.__factory(BytesIO(b''), self.__env)
            self.assertEqual(r.__class__, XMLRPCRequest)
            self.assertEqual(r.publication.__class__, XMLRPCPublication)

        # content type doesn't matter for non post
        for method in ('GET', 'HEAD', 'get', 'head'):
            self.__env['REQUEST_METHOD'] = method
            r = self.__factory(BytesIO(b''), self.__env)
            self.assertEqual(r.__class__, BrowserRequest)
            self.assertEqual(r.publication.__class__, BrowserPublication)

        for method in ('PUT', 'put', 'ZZZ'):
            self.__env['REQUEST_METHOD'] = method
            r = self.__factory(BytesIO(b''), self.__env)
            self.assertEqual(r.__class__, HTTPRequest)
            self.assertEqual(r.publication.__class__, HTTPPublication)
