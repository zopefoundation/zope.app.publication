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
""" Directive handlers

See metadirectives.py

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.app.publication.requestpublicationregistry import factoryRegistry
from zope.component.interface import provideInterface
from zope.component.zcml import handler
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces import IDefaultViewName


def publisher(_context, name, factory, methods=['*'], mimetypes=['*'],
              priority=0):

    factory = factory()

    for method in methods:
        for mimetype in mimetypes:
            _context.action(
                discriminator = (method, mimetype, priority),
                callable = factoryRegistry.register,
                args = (method, mimetype, name, priority, factory)
                )


def defaultView(_context, name, for_=None, layer=IBrowserRequest):

    _context.action(
        discriminator = ('defaultViewName', for_, layer, name),
        callable = handler,
        args = ('registerAdapter',
                name, (for_, layer), IDefaultViewName, '', _context.info)
        )

    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', for_)
            )
