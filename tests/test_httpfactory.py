##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
$Id: test_httpfactory.py,v 1.2 2003/02/11 15:59:53 sidnei Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.publication.httpfactory import HTTPPublicationRequestFactory
from zope.publisher.browser import BrowserRequest
from zope.app.publication.browser import BrowserPublication
from zope.publisher.http import HTTPRequest
from zope.app.publication.http import HTTPPublication
from zope.publisher.xmlrpc import XMLRPCRequest
from zope.app.publication.xmlrpc import XMLRPCPublication
from StringIO import StringIO

class Test(TestCase):

    def setUp(self):
        self.__factory = HTTPPublicationRequestFactory(None)
        self.__env =  {
            'SERVER_URL':         'http://127.0.0.1',
            'HTTP_HOST':          '127.0.0.1',
            'CONTENT_LENGTH':     '0',
            'GATEWAY_INTERFACE':  'TestFooInterface/1.0',
            }

    def test_browser(self):
        r = self.__factory(StringIO(''), StringIO(), self.__env)
        self.assertEqual(r.__class__, BrowserRequest)
        self.assertEqual(r.publication.__class__, BrowserPublication)

        for method in ('GET', 'HEAD', 'POST', 'get', 'head', 'post'):
            self.__env['REQUEST_METHOD'] = method
            r = self.__factory(StringIO(''), StringIO(), self.__env)
            self.assertEqual(r.__class__, BrowserRequest)
            self.assertEqual(r.publication.__class__, BrowserPublication)
            

    def test_http(self):

        for method in ('PUT', 'put', 'XXX'):
            self.__env['REQUEST_METHOD'] = method
            r = self.__factory(StringIO(''), StringIO(), self.__env)
            self.assertEqual(r.__class__, HTTPRequest)
            self.assertEqual(r.publication.__class__, HTTPPublication)

    def test_xmlrpc(self):
        self.__env['CONTENT_TYPE'] = 'text/xml'
        for method in ('POST', 'post'):
            self.__env['REQUEST_METHOD'] = method
            r = self.__factory(StringIO(''), StringIO(), self.__env)
            self.assertEqual(r.__class__, XMLRPCRequest)
            self.assertEqual(r.publication.__class__, XMLRPCPublication)


        # content type doesn't matter for non post
        for method in ('GET', 'HEAD', 'get', 'head'):
            self.__env['REQUEST_METHOD'] = method
            r = self.__factory(StringIO(''), StringIO(), self.__env)
            self.assertEqual(r.__class__, BrowserRequest)
            self.assertEqual(r.publication.__class__, BrowserPublication)

        for method in ('PUT', 'put', 'XXX'):
            self.__env['REQUEST_METHOD'] = method
            r = self.__factory(StringIO(''), StringIO(), self.__env)
            self.assertEqual(r.__class__, HTTPRequest)
            self.assertEqual(r.publication.__class__, HTTPPublication)

    
        

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
