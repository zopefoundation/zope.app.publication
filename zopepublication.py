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
import sys
import logging

from zope.component import getService
from zope.component.exceptions import ComponentLookupError
from zodb.interfaces import ConflictError

from zope.publisher.base import DefaultPublication
from zope.publisher.publish import mapply
from zope.publisher.interfaces import Retry

from zope.security.securitymanagement \
     import getSecurityManager, newSecurityManager
from zope.security.checker import ProxyFactory

from zope.proxy.introspection import removeAllProxies

from zope.app.interfaces.services.service import IServiceManagerContainer

from zope.exceptions import Unauthorized

from zope.app.applicationcontrol.applicationcontrol \
     import applicationControllerRoot

from zope.app.security.registries.principalregistry \
     import principalRegistry as prin_reg

from zope.app.interfaces.security import IUnauthenticatedPrincipal

from zope.app.publication.publicationtraverse import PublicationTraverse

from zope.proxy.context import ContextWrapper

# XXX Should this be imported here?
from transaction import get_transaction

class Cleanup:
    def __init__(self, f):
        self.__del__ = f


class ZopePublication(object, PublicationTraverse, DefaultPublication):
    """Base Zope publication specification."""

    version_cookie = 'Zope-Version'
    root_name = 'Application'

    def __init__(self, db):
        # db is a ZODB.DB.DB object.
        self.db = db

    def beforeTraversal(self, request):
        # Try to authenticate against the default global registry.
        p = prin_reg.authenticate(request)
        if p is None:
            p = prin_reg.unauthenticatedPrincipal()
            if p is None:
                raise Unauthorized # If there's no default principal

        newSecurityManager(p.getId())
        request.user = p
        get_transaction().begin()

    def _maybePlacefullyAuthenticate(self, request, ob):
        if not IUnauthenticatedPrincipal.isImplementedBy(request.user):
            # We've already got an authenticated user. There's nothing to do.
            # Note that beforeTraversal guarentees that user is not None.
            return

        if not IServiceManagerContainer.isImplementedBy(ob):
            # We won't find an authentication service here, so give up.
            return

        sm = removeAllProxies(ob).queryServiceManager()
        if sm is None:
            # No service manager here, and thus no auth service
            return

        sm = ContextWrapper(sm, ob, name="++etc++Services")

        auth_service = sm.get('Authentication')
        if auth_service is None:
            # No auth service here
            return

        # Try to authenticate against the auth service
        principal = auth_service.authenticate(request)
        if principal is None:
            principal = auth_service.unauthenticatedPrincipal()
            if principal is None:
                # nothing to do here
                return

        newSecurityManager(principal.getId())
        request.user = principal


    def callTraversalHooks(self, request, ob):
        # Call __before_publishing_traverse__ hooks

        # This is also a handy place to try and authenticate.
        self._maybePlacefullyAuthenticate(request, ob)

    def afterTraversal(self, request, ob):
        #recordMetaData(object, request)
        self._maybePlacefullyAuthenticate(request, ob)


    def openedConnection(self, conn):
        # Hook for auto-refresh
        pass

    def getApplication(self, request):

        # If the first name is '++etc++ApplicationControl', then we should
        # get it rather than look in the database!
        stack = request.getTraversalStack()

        if '++etc++ApplicationController' in stack:
            return applicationControllerRoot

        # Open the database.
        version = request.get(self.version_cookie, '')
        conn = self.db.open(version)

        cleanup = Cleanup(conn.close)
        request.hold(cleanup)  # Close the connection on request.close()

        self.openedConnection(conn)
##        conn.setDebugInfo(getattr(request, 'environ', None), request.other)

        root = conn.root()
        app = root.get(self.root_name, None)

        if app is None:
            raise SystemError, "Zope Application Not Found"

        return ProxyFactory(app)

    def getDefaultTraversal(self, request, ob):
        return ob, None

    def callObject(self, request, ob):
        return mapply(ob, request.getPositionalArguments(), request)

    def afterCall(self, request):
        txn = get_transaction()
        txn.note(request["PATH_INFO"])
        txn.setUser(getSecurityManager().getPrincipal())
        get_transaction().commit()

    def handleException(self, object, request, exc_info, retry_allowed=1):
        try:
            # Abort the transaction.
            get_transaction().abort()

            try:
                errService = getService(object,'ErrorReportingService')
            except ComponentLookupError:
                pass
            else:
                try:
                    errService.raising(exc_info, request)
                # It is important that an error in errService.raising
                # does not propagate outside of here. Otherwise, nothing
                # meaningful will be returned to the user.
                #
                # The error reporting service should not be doing database
                # stuff, so we shouldn't get a conflict error.
                # Even if we do, it is more important that we log this
                # error, and proceed with the normal course of events.
                # We should probably (somehow!) append to the standard
                # error handling that this error occurred while using
                # the ErrorReportingService, and that it will be in
                # the zope log.
                except:
                    logging.getLogger('SiteError').exception(
                        'Error while reporting an error to the '
                        'ErrorReportingService')

            # Delegate Unauthorized errors to the authentication service
            # XXX Is this the right way to handle Unauthorized?  We need
            # to understand this better.
            if isinstance(exc_info[1], Unauthorized):
                sm = getSecurityManager()
                id = sm.getPrincipal()
                prin_reg.unauthorized(id, request) # May issue challenge
                request.response.handleException(exc_info)
                return

            # XXX This is wrong. Should use getRequstView:
            #
            #
            # # Look for a component to handle the exception.
            # traversed = request.traversed
            # if traversed:
            #     context = traversed[-1]
            #     #handler = getExceptionHandler(context, t, IBrowserPublisher)
            #     handler = None  # no getExceptionHandler() exists yet.
            #     if handler is not None:
            #         handler(request, exc_info)
            #         return

            # Convert ConflictErrors to Retry exceptions.
            if retry_allowed and isinstance(exc_info[1], ConflictError):
                logger.getLogger('ZopePublication').warn(
                    'Competing writes/reads at %s',
                    request.get('PATH_INFO', '???'),
                    exc_info=True)
                raise Retry

            # Let the response handle it as best it can.
            # XXX Is this what we want in the long term?
            response = request.response
            response.handleException(exc_info)
            return
        finally:
            # Avoid leaking
            exc_info = 0


    def _parameterSetskin(self, pname, pval, request):
        request.setViewSkin(pval)

class DebugPublication(object):

    class call_wrapper:

        def __init__(self, ob):
            self.__ob = ob

        def __getattr__(self, name):
            return getattr(self.__ob, name)

        def __call__(self, *args, **kw):
            self.__ob(*args, **kw)

    def callObject(self, request, ob):
        return mapply(self.call_wrapper(ob),
                      request.getPositionalArguments(), request)
