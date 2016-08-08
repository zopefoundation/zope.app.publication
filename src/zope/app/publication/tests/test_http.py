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
"""Test HTTP Publication
"""
from unittest import TestCase, TestSuite, main, makeSuite
from io import BytesIO

from zope.interface import Interface, implementer
from zope.publisher.http import HTTPRequest
from zope.publisher.interfaces.http import IHTTPRequest

import zope.app.publication.http
from zope import component

class I(Interface):
    pass

@implementer(I)
class C(object):
    spammed = 0

class V(object):

    def __init__(self, context, request):
        self.context = context

    def SPAM(self):
        self.context.spammed += 1


class Test(TestCase):
    # Note that zope publication tests cover all of the code but callObject

    def test_callObject(self):
        pub = zope.app.publication.http.HTTPPublication(None)
        request = HTTPRequest(BytesIO(b''), {})
        request.method = 'SPAM'

        component.provideAdapter(V, (I, IHTTPRequest), Interface, name='SPAM')

        ob = C()
        pub.callObject(request, ob)
        self.assertEqual(ob.spammed, 1)


def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
