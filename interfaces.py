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


class ISOAPRequestFactory(interface.Interface):
    """SOAP request factory"""

    def __call__(input_stream, output_steam, env):
        """Create a request object to handle SOAP input."""


