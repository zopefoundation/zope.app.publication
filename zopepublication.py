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

from zope.component import queryView, queryDefaultViewName
from zope.component import queryService, queryAdapter
from zope.app.services.servicenames import ErrorLogging, Authentication
from zodb.interfaces import ConflictError

from zope.publisher.publish import mapply
from zope.publisher.interfaces import Retry, IExceptionSideEffects
from zope.publisher.interfaces.http import IHTTPRequest

from zope.security.management import newSecurityManager
from zope.security.checker import ProxyFactory

from zope.proxy.context import ContextWrapper

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

class Cleanup(object):
    def __init__(self, f):
        self._f = f

    def __del__(self):
        self._f()


class ZopePublication(object, PublicationTraverse):
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

        request.user = ContextWrapper(p, prin_reg)
        newSecurityManager(request.user)
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

        sm = ContextWrapper(sm, ob, name="++etc++site")

        auth_service = sm.queryService(Authentication)
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

        request.user = ContextWrapper(principal, auth_service)
        newSecurityManager(request.user)


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

        # If the first name is '++etc++process', then we should
        # get it rather than look in the database!
        stack = request.getTraversalStack()

        if '++etc++process' in stack:
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

        return ProxyFactory(ContextWrapper(app, None))

    def callObject(self, request, ob):
        return mapply(ob, request.getPositionalArguments(), request)

    def afterCall(self, request):
        txn = get_transaction()
        if IHTTPRequest.isImplementedBy(request):
            txn.note(request["PATH_INFO"])
        # XXX not sure why you would use id vs title or description
        txn.setUser(request.user.getId())
        get_transaction().commit()


    def _logErrorWithErrorReportingService(self, object, request, exc_info):
        # Record the error with the ErrorReportingService
        beginErrorHandlingTransaction(request, 'error reporting service')
        try:
            errService = queryService(object, ErrorLogging)
            if errService is not None:
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

            get_transaction().commit()
        except:
            tryToLogException(
                'Error while reporting an error to the %s service' %
                ErrorLogging)
            get_transaction().abort()


    def handleException(self, object, request, exc_info, retry_allowed=True):
        # This transaction had an exception that reached the publisher.
        # It must definitely be aborted.
        get_transaction().abort()

        # Convert ConflictErrors to Retry exceptions.
        if retry_allowed and isinstance(exc_info[1], ConflictError):
            tryToLogWarning('ZopePublication',
                'Competing writes/reads at %s' % 
                request.get('PATH_INFO', '???'),
                exc_info=True)
            raise Retry
        # Are there any reasons why we'd want to let application-level error
        # handling determine whether a retry is allowed or not?
        # Assume not for now.

        # Record the error with the ErrorReportingService
        self._logErrorWithErrorReportingService(object, request, exc_info)

        response = request.response
        response.reset()
        exception = None
        legacy_exception = not isinstance(exc_info[1], Exception)
        if legacy_exception:
            response.handleException(exc_info)
            if isinstance(exc_info[1], str):
                tryToLogWarning(
                    'Publisher received a legacy string exception: %s.'
                    ' This will be handled by the request.' %
                    exc_info[1])
            else:
                tryToLogWarning(
                    'Publisher received a legacy classic class exception: %s.'
                    ' This will be handled by the request.' %
                    exc_info[1].__class__)
        else:
            # We definitely have an Exception
            # Set the request body, and abort the current transaction.
            beginErrorHandlingTransaction(
                request, 'application error-handling')
            view = None
            try:
                exception = ContextWrapper(exc_info[1], object)
                name = queryDefaultViewName(exception, request)
                if name is not None:
                    view = queryView(exception, name, request)
            except:
                # Problem getting a view for this exception. Log an error.
                tryToLogException(
                    'Exception while getting view on exception')

            if view is not None:
                try:
                    response.setBody(self.callObject(request, view))
                    get_transaction().commit()
                except:
                    # Problem rendering the view for this exception.
                    # Log an error.
                    tryToLogException(
                        'Exception while rendering view on exception')

                    # Record the error with the ErrorReportingService
                    self._logErrorWithErrorReportingService(
                        object, request, sys.exc_info())

                    view = None

            if view is None:
                # Either the view was not found, or view was set to None
                # because the view couldn't be rendered. In either case,
                # we let the request handle it.
                response.handleException(exc_info)
                get_transaction().abort()

            # See if there's an IExceptionSideEffects adapter for the
            # exception
            try:
                adapter = queryAdapter(exception, IExceptionSideEffects)
            except:
                tryToLogException(
                    'Exception while getting IExceptionSideEffects adapter')
                adapter = None

            if adapter is not None:
                beginErrorHandlingTransaction(
                    request, 'application error-handling side-effect')
                try:
                    # Although request is passed in here, it should be
                    # considered read-only.
                    adapter(object, request, exc_info)
                    get_transaction().commit()
                except:
                    tryToLogException(
                        'Exception while calling'
                        ' IExceptionSideEffects adapter')
                    get_transaction().abort()

    def _parameterSetskin(self, pname, pval, request):
        request.setViewSkin(pval)

def tryToLogException(arg1, arg2=None):
    if arg2 is None:
        subsystem = 'SiteError'
        message = arg1
    else:
        subsystem = arg1
        message = arg2
    try:
        logging.getLogger(subsystem).exception(message)
    # Bare except, because we want to swallow any exception raised while
    # logging an exception.
    except:
        pass

def tryToLogWarning(arg1, arg2=None, exc_info=False):
    if arg2 is None:
        subsystem = 'SiteError'
        message = arg1
    else:
        subsystem = arg1
        message = arg2
    try:
        logging.getLogger(subsystem).warn(message, exc_info=exc_info)
    # Bare except, because we want to swallow any exception raised while
    # logging a warning.
    except:
        pass

def beginErrorHandlingTransaction(request, note):
    get_transaction().begin()
    if IHTTPRequest.isImplementedBy(request):
        pathnote = '%s ' % request["PATH_INFO"]
    else:
        pathnote = ''
    get_transaction().note(
        '%s(%s)' % (pathnote, note))
