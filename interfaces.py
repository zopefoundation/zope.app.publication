##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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

$Id$
"""

from zope.interface import Interface


class IPublicationRequestFactoryFactory(Interface):
    """Publication request factory factory"""

    def realize(db):
        """Create a publication and request factory for a given database

        Return a IPublicationRequestFactory for the given database.
        """


class IPublicationRequestFactory(Interface):
    """Publication request factory"""

    def __call__(input_stream, output_steam, env):
        """Create a request object to handle the given inputs

        A request is created and configured with a publication object.
        """


class IRequestFactory(IPublicationRequestFactory,
                      IPublicationRequestFactoryFactory):
    """This is a pure read-only interface, since the values are set through
       a ZCML directive and we shouldn't be able to change them.
    """
