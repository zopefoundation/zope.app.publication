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
"""Test HTTP Publication

$Id$
"""
from unittest import TestCase, TestSuite, main, makeSuite
from zope.app import zapi
import zope.app.publication.http
from zope.publisher.http import HTTPRequest
from zope.app.tests.placelesssetup import PlacelessSetup
from StringIO import StringIO
from zope.interface import Interface, implements
from zope.publisher.interfaces.http import IHTTPRequest

class I(Interface): pass
class C(object):
    spammed = 0
    implements(I)

class V(object):

    def __init__(self, context, request):
        self.context = context

    def SPAM(self):
        self.context.spammed += 1


class Test(PlacelessSetup, TestCase):
    # Note that zope publication tests cover all of the code but callObject

    def test_callObject(self):
        pub = zope.app.publication.http.HTTPPublication(None)
        request = HTTPRequest(StringIO(''), StringIO(), {})
        request.method = 'SPAM'

        s = zapi.getGlobalService(zapi.servicenames.Presentation)
        s.provideView(I, 'SPAM', IHTTPRequest, V)

        ob = C()
        pub.callObject(request, ob)
        self.assertEqual(ob.spammed, 1)


def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
