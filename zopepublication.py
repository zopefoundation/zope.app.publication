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
"""Zope publication

$Id$
"""
import sys
import logging
from new import instancemethod

from ZODB.POSException import ConflictError

from zope.interface import implements, providedBy
from zope.component import getService
from zope.app.servicenames import ErrorLogging
from zope.component.exceptions import ComponentLookupError
from zope.publisher.publish import mapply
from zope.publisher.interfaces import Retry, IExceptionSideEffects
from zope.publisher.interfaces import IRequest, IPublication

from zope.security.management import newInteraction, endInteraction
from zope.security.checker import ProxyFactory
from zope.security.proxy import trustedRemoveSecurityProxy
from zope.proxy import removeAllProxies
from zope.exceptions import Unauthorized

from zope.app import zapi
from zope.app.site.interfaces import ISite
from zope.app.applicationcontrol.applicationcontrol \
     import applicationControllerRoot

from zope.app.servicenames import ErrorLogging, Authentication
from zope.app.security.principalregistry import principalRegistry as prin_reg
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.publication.publicationtraverse import PublicationTraverse
from zope.app.traversing.interfaces import IPhysicallyLocatable
from zope.app.location import LocationProxy
from zope.app.event import publish
from zope.app.publication.interfaces import BeforeTraverseEvent
from zope.app.publication.interfaces import EndRequestEvent

class Cleanup(object):

    def __init__(self, f):
        self._f = f

    def __del__(self):
        self._f()

class ZopePublication(PublicationTraverse):
    """Base Zope publication specification."""
    implements(IPublication)

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

        request.setPrincipal(p)
        newInteraction(request)
        get_transaction().begin()

    def _maybePlacefullyAuthenticate(self, request, ob):
        if not IUnauthenticatedPrincipal.providedBy(request.principal):
            # We've already got an authenticated user. There's nothing to do.
            # Note that beforeTraversal guarentees that user is not None.
            return

        if not ISite.providedBy(ob):
            # We won't find an authentication service here, so give up.
            return

        sm = removeAllProxies(ob).getSiteManager()

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

        request.setPrincipal(principal)

    def callTraversalHooks(self, request, ob):
        # Call __before_publishing_traverse__ hooks
        publish(None, BeforeTraverseEvent(ob, request))
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
        #conn.setDebugInfo(getattr(request, 'environ', None), request.other)

        root = conn.root()
        app = root.get(self.root_name, None)

        if app is None:
            raise SystemError, "Zope Application Not Found"

        return ProxyFactory(app)

    def callObject(self, request, ob):
        return mapply(ob, request.getPositionalArguments(), request)

    def afterCall(self, request, ob):
        txn = get_transaction()
        self.annotateTransaction(txn, request, ob)

        txn.commit()

    def endRequest(self, request, ob):
        endInteraction()
        publish(None, EndRequestEvent(ob, request))

    def annotateTransaction(self, txn, request, ob):
        """Set some useful meta-information on the transaction. This
        information is used by the undo framework, for example.

        This method is not part of the IPublication interface, since
        it's specific to this particular implementation.
        """
        txn.setUser(request.principal.id)

        # Work around methods that are usually used for views
        bare = trustedRemoveSecurityProxy(ob)
        if isinstance(bare, instancemethod):
            ob = bare.im_self

        # set the location path
        path = None
        locatable = IPhysicallyLocatable(ob, None)
        if locatable is not None:
            # Views are made children of their contexts, but that
            # doesn't necessarily mean that we can fully resolve the
            # path. E.g. the family tree of a resource cannot be
            # resolved completely, as the presentation service is a
            # dead end.
            try:
                path = locatable.getPath()
            except AttributeError:
                pass
        if path is not None:
            txn.setExtendedInfo('location', path)

        # set the request type
        iface = IRequest
        for iface in providedBy(request):
            if iface.extends(IRequest):
                break
        iface_dotted = iface.__module__ + '.' + iface.getName()
        txn.setExtendedInfo('request_type', iface_dotted)
        return txn

    def _logErrorWithErrorReportingService(self, object, request, exc_info):
        # Record the error with the ErrorReportingService
        self.beginErrorHandlingTransaction(request, object,
                                           'error reporting service')
        try:
            try:
                errService = getService(ErrorLogging)
                errService.raising(exc_info, request)
            except ComponentLookupError:
                # There is no local error reporting service.
                # XXX We need to build a local error reporting service.
                pass
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
            self.beginErrorHandlingTransaction(
                request, object, 'application error-handling')
            view = None
            try:
                # XXX we need to get a location. The object might not
                # have one, because it might be a method. If we don't
                # have a parent attr but have an im_self or an
                # __self__, use that:
                loc = object
                if hasattr(object, '__parent__'):
                    loc = object
                else:
                    loc = removeAllProxies(object)
                    loc = getattr(loc, 'im_self', loc)
                    if loc is loc:
                        loc = getattr(loc, '__self__', loc)
                    loc = ProxyFactory(loc)

                exception = LocationProxy(exc_info[1], loc)
                name = zapi.queryDefaultViewName(exception, request)
                if name is not None:
                    view = zapi.queryView(exception, name, request)
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
                adapter = IExceptionSideEffects(exception, None)
            except:
                tryToLogException(
                    'Exception while getting IExceptionSideEffects adapter')
                adapter = None

            if adapter is not None:
                self.beginErrorHandlingTransaction(
                    request, object, 'application error-handling side-effect')
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

    def beginErrorHandlingTransaction(self, request, ob, note):
        txn = get_transaction()
        txn.begin()
        txn.note(note)
        self.annotateTransaction(txn, request, ob)
        return txn

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
