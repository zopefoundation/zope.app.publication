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
"""Publication factories.

This module provides factories for tuples (request, publication).

$Id: xmlrpc.py 27311 2004-08-27 21:22:43Z jim $
"""
__docformat__ = 'restructuredtext'

from zope import component
from zope.interface import implements
from zope.app.publication.http import BaseHTTPPublication
from zope.app.publication.interfaces import IRequestPublicationFactory, ISOAPRequestFactory, ISOAPRequestFactory
from zope.app.publication import interfaces
from zope.app.publication.soap import SOAPPublication

class SOAPFactory(object):

    implements(IRequestPublicationFactory)

    def canHandle(self, environment):
        self.soap_req = component.queryUtility(interfaces.ISOAPRequestFactory)
        return bool(environment.get('HTTP_SOAPACTION') and self.soap_req)

    def getRequestPublication(self):
        return self.soap_req, SOAPPublication

