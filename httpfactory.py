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
from zope.app.zapi import getUtility, getSiteManager

from zope.component.adapter import GlobalAdapterService
from zope.component.exceptions import ComponentLookupError

from zope.app.publication.publicationfactories import HTTPFactory, BrowserFactory


def chooseClasses(method, environment, context=None):
    """ see README.txt """
    def _byname(chooser1, chooser2):
        """ reverse sorting """
        return cmp(chooser2.getSortKey(), chooser1.getSortKey())

    try:
        method_interface = getUtility(interfaces.IMethodBase, method)
    except ComponentLookupError:
        # unhandled method, returns http publisher
        return HTTPFactory()()

    content_type = environment.get('CONTENT_TYPE', '')

    try:
        content_type_interface = getUtility(interfaces.IMimetypeBase, content_type)
    except ComponentLookupError:
        # unhandled mimetype, returns browser publisher
        return BrowserFactory()()

    # do a lookup here, returns a list callables
    adapters = getSiteManager(context).adapters

    choosers = adapters.lookupAll(required=(method_interface,
                                            content_type_interface),
                                  provided=interfaces.IRequestPublicationFactory)

    # choose a chooser here
    # chooser sorting, to sort from most specialized to less
    choosers = [chooser[1] for chooser in list(choosers)]
    choosers.sort(_byname)

    for chooser in choosers:
        if chooser.canHandle(environment):
            return chooser()

    return BrowserFactory()() 

class HTTPPublicationRequestFactory(object):
    interface.implements(interfaces.IPublicationRequestFactory)

    def __init__(self, db):
        """See `zope.app.publication.interfaces.IPublicationRequestFactory`"""
        self._db = db
        self._publication_cache = {}

    def __call__(self, input_stream, env, output_stream=None):
        """See `zope.app.publication.interfaces.IPublicationRequestFactory`"""
        # BBB: This is backward-compatibility support for the deprecated
        # output stream.
        try:
            env.get
        except AttributeError:
            import warnings
            warnings.warn("Can't pass output streams to requests anymore. "
                          "This will go away in Zope 3.4.",
                          DeprecationWarning,
                          2)
            env, output_stream = output_stream, env


        method = env.get('REQUEST_METHOD', 'GET').upper()
        request_class, publication_class = chooseClasses(method, env, self._db)

        publication = self._publication_cache.get(publication_class)
        if publication is None:
            publication = publication_class(self._db)
            self._publication_cache[publication_class] = publication

        request = request_class(input_stream, env)
        request.setPublication(publication)
        if IBrowserRequest.providedBy(request):
            # only browser requests have skins
            setDefaultSkin(request)
        return request
