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
$Id: test_http.py,v 1.2 2003/02/11 15:59:53 sidnei Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
import zope.app.publication.http
from zope.publisher.http import HTTPRequest
from zope.app.tests.placelesssetup import PlacelessSetup
from StringIO import StringIO
from zope.component.view import provideView
from zope.interface import Interface
from zope.publisher.interfaces.http import IHTTPPresentation

class I(Interface): pass
class C:
    spammed = 0
    __implements__ = I

class V:

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
        provideView(I, 'SPAM', IHTTPPresentation, V)

        ob = C()
        pub.callObject(request, ob)
        self.assertEqual(ob.spammed, 1)

        

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
