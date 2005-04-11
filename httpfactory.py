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

from zope.app import zapi
from zope.app.publication.interfaces import IPublicationRequestFactory
from zope.app.publication.http import HTTPPublication
from zope.app.publication.browser import BrowserPublication, setDefaultSkin
from zope.app.publication.xmlrpc import XMLRPCPublication
from zope.app.publication.soap import SOAPPublication
from zope.app.publication.interfaces import ISOAPRequestFactory

_browser_methods = 'GET', 'POST', 'HEAD'

class HTTPPublicationRequestFactory(object):
    implements(IPublicationRequestFactory)

    def __init__(self, db):
        """See `zope.app.publication.interfaces.IPublicationRequestFactory`"""
        self._http = HTTPPublication(db)
        self._brower = BrowserPublication(db)
        self._xmlrpc = XMLRPCPublication(db)
        self._soappub = SOAPPublication(db)
        self._soapreq = zapi.queryUtility(ISOAPRequestFactory)

    def __call__(self, input_stream, output_steam, env):
        """See `zope.app.publication.interfaces.IPublicationRequestFactory`"""
        method = env.get('REQUEST_METHOD', 'GET').upper()

        if method in _browser_methods:
            content_type = env.get('CONTENT_TYPE', '')
            is_xml = content_type.startswith('text/xml')

            if (method == 'POST' and is_xml and
                env.get('HTTP_SOAPACTION', None)
                and self._soapreq is not None):
                request = self._soapreq(input_stream, output_steam, env)
                request.setPublication(self._soappub)
            elif (method == 'POST' and is_xml):
                request = XMLRPCRequest(input_stream, output_steam, env)
                request.setPublication(self._xmlrpc)
            else:
                request = BrowserRequest(input_stream, output_steam, env)
                request.setPublication(self._brower)
                setDefaultSkin(request)
        else:
            request = HTTPRequest(input_stream, output_steam, env)
            request.setPublication(self._http)

        return request
