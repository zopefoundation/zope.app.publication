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
""" Directive handler for publication factory

See metadirective.py

$Id: $
"""
__docformat__ = 'restructuredtext'

from zope.app.publication.requestpublicationregistry import RequestPublicationRegistry

class RequestPublicationRegisterer(object):
    """ Link a request type to a request-publication factory """

    def __init__(self, name, factory, method=u'', mimetype=u'', priority=0):

        methods = self._extractElements(method)
        mimetypes = self._extractElements(mimetype)
        self._installFactory(name, factory, methods, mimetypes, priority)  

    def _extractElements(self, chain):
        """ elements are separated by commas,

        >>> reg = RequestPublicationRegisterer()
        >>> reg._extractElements('GET, POST,HEAD')
        ['GET', 'POST', 'HEAD']
        >>> reg._extractElements('*')
        ['*']
        >>> reg._extractElements('')
        ['*']
        >>> reg._extractElements('text/xml, text/html')
        ['text/xml', 'text/html']
        """
        def _cleanElement(element):
            element = element.strip()
            if element == u'':
                return u'*'
            return element

        return map(_cleanElement, chain.split(u','))

    def _installFactory(self, name, factory, methods, mimetypes, priority):
        """ calls the register factory utility, that actually links
            the factory.
        """
        registerer = _factory_registerer.register

        # need to register all methods<->mimetypes combos here
        # for imbrication: usally there are more methods than mimetypes
        for method in methods:
            for mimetype in mimetypes:
                registerer(method, mimetype, name, priority, factory)

_factory_registerer = None

def getFactoryRegistry():
    return _factory_registerer

def publisher(_context, name, factory, method='*', mimetype='*', priority=0):

    global _factory_registerer
    if _factory_registerer is None:
        _factory_registerer = RequestPublicationRegistry()

    RequestPublicationRegisterer(name, factory(), method, mimetype, priority)
