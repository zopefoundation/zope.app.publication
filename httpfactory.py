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
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""HTTP Factory

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import implements
from zope.publisher.http import HTTPRequest
from zope.publisher.browser import BrowserRequest
from zope.publisher.xmlrpc import XMLRPCRequest

from zope.app.publication.interfaces import IPublicationRequestFactory

from zope.app.publication.http import HTTPPublication
from zope.app.publication.browser import BrowserPublication
from zope.app.publication.xmlrpc import XMLRPCPublication

_browser_methods = 'GET', 'POST', 'HEAD'

class HTTPPublicationRequestFactory(object):
    implements(IPublicationRequestFactory)

    def __init__(self, db):
        """See `zope.app.publication.interfaces.IPublicationRequestFactory`"""
        self._http = HTTPPublication(db)
        self._brower = BrowserPublication(db)
        self._xmlrpc = XMLRPCPublication(db)

    def __call__(self, input_stream, output_steam, env):
        """See `zope.app.publication.interfaces.IPublicationRequestFactory`"""
        method = env.get('REQUEST_METHOD', 'GET').upper()

        if method in _browser_methods:
            if (method == 'POST' and
                env.get('CONTENT_TYPE', '').startswith('text/xml')
                ):
                request = XMLRPCRequest(input_stream, output_steam, env)
                request.setPublication(self._xmlrpc)
            else:
                request = BrowserRequest(input_stream, output_steam, env)
                request.setPublication(self._brower)
        else:
            request = HTTPRequest(input_stream, output_steam, env)
            request.setPublication(self._http)

        return request
