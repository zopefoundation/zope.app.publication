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

from zope.component import getService, getView, getDefaultViewName
from zope.component import queryService, getAdapter
from zope.component.exceptions import ComponentLookupError
from zope.component.servicenames import ErrorReports, Authentication
from zodb.interfaces import ConflictError

from zope.publisher.publish import mapply
from zope.publisher.interfaces import Retry, IExceptionSideEffects
from zope.publisher.interfaces.http import IHTTPRequest

from zope.security.management import getSecurityManager, newSecurityManager
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

        newSecurityManager(p.getId())
        # XXX add a test to check that request.user is context wrapped
        request.user = ContextWrapper(p, prin_reg)
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

        auth_service = sm.get(Authentication)
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
        # XXX add test that request.user is context-wrapped
        request.user = ContextWrapper(principal, auth_service)


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

    def callObject(self, request, ob):
        return mapply(ob, request.getPositionalArguments(), request)

    def afterCall(self, request):
        txn = get_transaction()
        if IHTTPRequest.isImplementedBy(request):
            txn.note(request["PATH_INFO"])
        # XXX not sure why you would use id vs title or description
        txn.setUser(request.user.getId())
        get_transaction().commit()

    def handleException(self, object, request, exc_info, retry_allowed=True):
        # Convert ConflictErrors to Retry exceptions.
        if retry_allowed and isinstance(exc_info[1], ConflictError):
            get_transaction().abort()
            tryToLogWarning('ZopePublication',
                'Competing writes/reads at %s' % 
                request.get('PATH_INFO', '???'),
                exc_info=True)
            raise Retry
        # Are there any reasons why we'd want to let application-level error
        # handling determine whether a retry is allowed or not?
        # Assume not for now.

        response = request.response
        exception = None
        legacy_exception = not isinstance(exc_info[1], Exception)
        if legacy_exception:
            response.handleException(exc_info)
            get_transaction().abort()
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
            try:
                # Set the request body, and abort the current transaction.
                try:
                    exception = ContextWrapper(exc_info[1], object)
                    name = getDefaultViewName(exception, request)
                    view = getView(exception, name, request)
                    response.setBody(self.callObject(request, view))
                except ComponentLookupError:
                    # No view available for this exception, so let the
                    # response handle it.
                    response.handleException(exc_info)
                except:
                    # Problem getting a view for this exception. Log an error.
                    tryToLogException(
                        'Exception while getting view on exception')
                    # So, let the response handle it.
                    response.handleException(exc_info)
            finally:
                # Definitely abort the transaction that raised the exception.
                get_transaction().abort()

        # New transaction for side-effects
        beginErrorHandlingTransaction(request)
        transaction_ok = False

        # Record the error with the ErrorReportingService
        try:
            errService = queryService(object, ErrorReports)
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

        except:
            tryToLogException(
                'Error while reporting an error to the %s service' %
                ErrorReports)
            get_transaction().abort()
            beginErrorHandlingTransaction(request)

        if legacy_exception:
            # There should be nothing of consequence done in this transaction,
            # but this allows the error reporting service to save things
            # persistently when we get a legacy exception.
            get_transaction().commit()
        else:
            # See if there's an IExceptionSideEffects adapter for the
            # exception
            try:
                adapter = getAdapter(exception, IExceptionSideEffects)
                # view_presented is None if no view was presented, or the name
                # of the view, if it was.
                # Although request is passed in here, it should be considered
                # read-only.
                adapter(object, request, exc_info)
                get_transaction().commit()
            except:
                get_transaction().abort()

        return

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

def beginErrorHandlingTransaction(request):
    get_transaction().begin()
    if IHTTPRequest.isImplementedBy(request):
        pathnote = '%s ' % request["PATH_INFO"]
    else:
        pathnote = ''
    get_transaction().note(
        '%s(application error handling)' % pathnote)
