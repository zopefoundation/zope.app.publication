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

from zope import component, interface

from zope.publisher.http import HTTPRequest
from zope.publisher.browser import BrowserRequest
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.xmlrpc import XMLRPCRequest

from zope.app.publication import interfaces
from zope.app.publication.http import HTTPPublication
from zope.app.publication.browser import BrowserPublication, setDefaultSkin
from zope.app.publication.xmlrpc import XMLRPCPublication
from zope.app.publication.soap import SOAPPublication


def chooseClasses(method, environment):
    if method in ('GET', 'POST', 'HEAD'):
        content_type = environment.get('CONTENT_TYPE', '')
        is_xml = content_type.startswith('text/xml')

        soap_request = component.queryUtility(interfaces.ISOAPRequestFactory)
        if (method == 'POST' and is_xml and environment.get('HTTP_SOAPACTION')
        and soap_request is not None):
            request_class = soap_request
            publication_class = SOAPPublication
        elif (method == 'POST' and is_xml):
            request_class = component.queryUtility(
                interfaces.IXMLRPCRequestFactory, default=XMLRPCRequest)
            publication_class = XMLRPCPublication
        else:
            request_class = component.queryUtility(
                interfaces.IBrowserRequestFactory, default=BrowserRequest)
            publication_class = BrowserPublication
    else:
        request_class = component.queryUtility(
            interfaces.IHTTPRequestFactory, default=HTTPRequest)
        publication_class = HTTPPublication

    return request_class, publication_class


class HTTPPublicationRequestFactory(object):
    interface.implements(interfaces.IPublicationRequestFactory)

    def __init__(self, db):
        """See `zope.app.publication.interfaces.IPublicationRequestFactory`"""
        self._db = db

    def __call__(self, input_stream, output_steam, env):
        """See `zope.app.publication.interfaces.IPublicationRequestFactory`"""
        method = env.get('REQUEST_METHOD', 'GET').upper()
        request_class, publication_class = chooseClasses(method, env)
        request = request_class(input_stream, output_steam, env)
        request.setPublication(publication_class(self._db))
        if IBrowserRequest.providedBy(request):
            # only browser requests have skins
            setDefaultSkin(request)
        return request
