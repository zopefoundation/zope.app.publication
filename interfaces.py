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

from zope.interface import implements, Interface

class IPublicationRequestFactory(Interface):
    """Publication request factory"""

    def __call__(input_stream, output_steam, env):
        """Create a request object to handle the given inputs

        A request is created and configured with a publication object.
        """

class IBeforeTraverseEvent(Interface):
    """An event which gets sent on publication traverse"""


class BeforeTraverseEvent(object):
    """An event which gets sent on publication traverse"""
    implements(IBeforeTraverseEvent)
    def __init__(self, ob, request):
        self.object = ob
        self.request = request


class IEndRequestEvent(Interface):
    """An event which gets sent when the publication is ended"""


class EndRequestEvent(object):
    """An event which gets sent when the publication is ended"""
    implements(IEndRequestEvent)
    def __init__(self, ob, request):
        self.object = ob
        self.request = request
