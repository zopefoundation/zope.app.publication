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
""" Directive schema, for publication factory

This module provides the schema for the new zcml directive,
that let the developer associate a publication factory to a given
request, based on its method and mimetype.

Each directive also has a name and a sortkey.

The sortkey helps when several directives can handle a request:
they are sorted by this key and the highest one is taken.

$Id: $
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface
from zope.configuration.fields import GlobalObject
from zope.schema import TextLine, Int

class IRequestPublicationDirective(Interface):
    """ Link a request type to a request-publication factory """

    name = TextLine(title=u'Name',
                    description=u'The name of the publication factory.')

    factory = GlobalObject(title=u'Factory',
                           description=u'The request-publication factory')

    method = TextLine(title=u'Method',
                      description=(u'The name of the request method.'
                                    'The method can be a "*" for'
                                    'the publication to catch all method'
                                    'otherwise, has to be one or many methods'
                                    'all separated by commas: ie: "GET,POST"'),
                      required=False)

    mimetype = TextLine(title=u'MimeType',
                        description=(u'The content type of the request.'
                                      'The method can be a "*" for'
                                      'the publication to catch all method'
                                      'otherwise, has to be one or many methods'
                                      'all separated by commas: ie: "text/xml,text/html"'),
                        required=False)

    priority = Int(title=u'Priority',
                   description=(u'A priority key used to concurrent'
                                 ' publication factories.'),
                   required=False)
