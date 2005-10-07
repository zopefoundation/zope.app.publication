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
"""Publication Interfaces

$Id$
"""
__docformat__ = 'restructuredtext'

from zope import interface
import zope.app.event.interfaces

class IPublicationRequestFactory(interface.Interface):
    """Publication request factory"""

    def __call__(input_stream, output_steam, env):
        """Create a request object to handle the given inputs

        A request is created and configured with a publication object.
        """

class IBeforeTraverseEvent(zope.app.event.interfaces.IObjectEvent):
    """An event which gets sent on publication traverse"""

    request = interface.Attribute("The current request")

class BeforeTraverseEvent(object):
    """An event which gets sent on publication traverse"""

    interface.implements(IBeforeTraverseEvent)

    def __init__(self, ob, request):
        self.object = ob
        self.request = request


class IEndRequestEvent(interface.Interface):
    """An event which gets sent when the publication is ended"""


class EndRequestEvent(object):
    """An event which gets sent when the publication is ended"""

    interface.implements(IEndRequestEvent)

    def __init__(self, ob, request):
        self.object = ob
        self.request = request

class IRequestFactory(interface.Interface):

    def __call__(input_stream, output_steam, env):
        """Create a request object to handle input."""

class ISOAPRequestFactory(IRequestFactory):
    """SOAP request factory"""

class IHTTPRequestFactory(IRequestFactory):
    # TODO: should SOAP, XMLRPC, and Browser extend this?
    """generic HTTP request factory"""

class IXMLRPCRequestFactory(IRequestFactory):
    """XMLRPC request factory"""

class IBrowserRequestFactory(IRequestFactory):
    """browser request factory"""

class IFileContent(interface.Interface):
    """Marker interface for content that can be managed as files.

    The default view for file content has effective URLs that don't end in
    /.  In particular, if the content included HTML, relative links in
    the HTML are relative to the container the content is in.
    """


# marker interfaces for request-publication factories
class IMethodBase(interface.interfaces.IInterface):
    """ interface for all request-publication factories """

class IMethodPOST(interface.Interface):
    """Marker interface for request-publication factories able to deal
       with POST requests.
    """
interface.directlyProvides(IMethodPOST, IMethodBase)

class IMethodGET(interface.Interface):
    """Marker interface for request-publication factories able to deal
       with GET requests.
    """
interface.directlyProvides(IMethodGET, IMethodBase)

class IMethodHEAD(interface.Interface):
    """Marker interface for request-publication factories able to deal
       with HEAD requests.
    """
interface.directlyProvides(IMethodHEAD, IMethodBase)

# marker interfaces for request-chooser factories
class IMimetypeBase(interface.interfaces.IInterface):
    """Base interface for all request-choosers """

class IMimetypeTextXML(interface.Interface):
    """ request-chooser able to deal with text/html """
interface.directlyProvides(IMimetypeTextXML, IMimetypeBase)

class IRequestPublicationFactory(IMimetypeBase):
    """ request-publication factory """

    def canHandle(environment):
        """ returns True if it can handle the request,
            otherwise False. 'environment' can be used by the factory 
            to make a decision based on the HTTP headers.
        """

    def __call__():
        """ returns a tuple (request, publication) """

    def getSortKey():
        """ returns a string that is used to sort the factories
            when several factories can handle the request.

            After a sort, the highest one gets picked
        """
