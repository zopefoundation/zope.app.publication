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
"""Zope Publication Tests

$Id$
"""
import unittest
import sys
from cStringIO import StringIO

from persistent import Persistent
from ZODB.DB import DB
from ZODB.DemoStorage import DemoStorage
import transaction

from zope.interface.verify import verifyClass
from zope.interface import implements, classImplements, implementedBy
from zope.i18n.interfaces import IUserPreferredCharsets
from zope.component import getGlobalServices
from zope.component.interfaces import IServiceService
from zope.component.exceptions import ComponentLookupError
from zope.publisher.base import TestPublication, TestRequest
from zope.publisher.http import IHTTPRequest, HTTPCharsets
from zope.publisher.interfaces import IRequest, IPublishTraverse
from zope.publisher.browser import BrowserResponse
from zope.security import simplepolicies
from zope.security.management import setSecurityPolicy, queryInteraction

from zope.app import zapi
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.tests import setup
from zope.app.tests import ztapi

from zope.app.errorservice.interfaces import IErrorReportingService
from zope.app.servicenames import ErrorLogging, Authentication
from zope.app.location.interfaces import ILocation
from zope.app.traversing.interfaces import IPhysicallyLocatable
from zope.app.security.principalregistry import principalRegistry
from zope.app.security.interfaces import IUnauthenticatedPrincipal, IPrincipal
from zope.app.publication.zopepublication import ZopePublication
from zope.app.folder import Folder, rootFolder
from zope.app.location import Location

class Principal(object):
    implements(IPrincipal)
    def __init__(self, id):
        self.id = id
        self.title = ''
        self.description = ''

class UnauthenticatedPrincipal(Principal):
    implements(IUnauthenticatedPrincipal)

class AuthService1(object):

    def authenticate(self, request):
        return None

    def unauthenticatedPrincipal(self):
        return UnauthenticatedPrincipal('test.anonymous')

    def unauthorized(self, id, request):
        pass

    def getPrincipal(self, id):
        return UnauthenticatedPrincipal(id)

class AuthService2(AuthService1):

    def authenticate(self, request):
        return Principal('test.bob')

    def getPrincipal(self, id):
        return Principal(id)

class ErrorLoggingService(object):
    implements(IErrorReportingService)

    def __init__(self):
        self.exceptions = []

    def raising(self, info, request=None):
        self.exceptions.append([info, request])

class ServiceManager(object):
    implements(IServiceService) # a dirty lie

    def __init__(self, auth):
        self.auth = auth

    def getService(self, name):
        if name == Authentication:
            return self.auth
        raise ComponentLookupError(name)

class LocatableObject(Location):

    def foo(self):
        pass

class BasePublicationTests(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(BasePublicationTests, self).setUp()
        from zope.security.management import endInteraction
        endInteraction()
        ztapi.provideAdapter(IHTTPRequest, IUserPreferredCharsets,
                             HTTPCharsets)
        self.policy = setSecurityPolicy(
            simplepolicies.PermissiveSecurityPolicy
            )
        self.storage = DemoStorage('test_storage')
        self.db = db = DB(self.storage)

        connection = db.open()
        root = connection.root()
        app = getattr(root, ZopePublication.root_name, None)

        if app is None:
            from zope.app.folder import rootFolder
            app = rootFolder()
            root[ZopePublication.root_name] = app
            transaction.commit()

        connection.close()
        self.app = app

        from zope.app.traversing.namespace import view, resource, etc
        ztapi.provideNamespaceHandler('view', view)
        ztapi.provideNamespaceHandler('resource', resource)
        ztapi.provideNamespaceHandler('etc', etc)

        self.out = StringIO()
        self.request = TestRequest('/f1/f2', outstream=self.out)
        self.user = Principal('test.principal')
        self.request.setPrincipal(self.user)
        from zope.interface import Interface
        self.presentation_type = Interface
        self.request._presentation_type = self.presentation_type
        self.object = object()
        self.publication = ZopePublication(self.db)

    def tearDown(self):
        setSecurityPolicy(self.policy) # XXX still needed?
        super(BasePublicationTests, self).tearDown()

    def testInterfacesVerify(self):
        for interface in implementedBy(ZopePublication):
            verifyClass(interface, TestPublication)


class ZopePublicationErrorHandling(BasePublicationTests):

    def testRetryAllowed(self):
        from ZODB.POSException import ConflictError
        from zope.publisher.interfaces import Retry
        try:
            raise ConflictError
        except:
            pass
        self.assertRaises(Retry, self.publication.handleException,
            self.object, self.request, sys.exc_info(), retry_allowed=True)

    def testRetryNotAllowed(self):
        from ZODB.POSException import ConflictError
        try:
            raise ConflictError
        except:
            pass
        self.publication.handleException(
            self.object, self.request, sys.exc_info(), retry_allowed=False)
        self.request.response.outputBody()
        value = self.out.getvalue().split()
        self.assertEqual(' '.join(value[:6]),
                         'Traceback (most recent call last): File')
        self.assertEqual(' '.join(value[-8:]),
                         'in testRetryNotAllowed raise ConflictError'
                         ' ConflictError: database conflict error')

    def testViewOnException(self):
        from ZODB.POSException import ConflictError
        from zope.interface import Interface
        class IConflictError(Interface):
            pass
        classImplements(ConflictError, IConflictError)
        s = zapi.getGlobalService(zapi.servicenames.Presentation)
        s.setDefaultViewName(IConflictError,
                             self.presentation_type, 'name')
        view_text = 'You had a conflict error'
        s = zapi.getGlobalService(zapi.servicenames.Presentation) 
        s.provideView(IConflictError, 'name', self.presentation_type,
                      lambda obj, request: lambda: view_text)
        try:
            raise ConflictError
        except:
            pass
        self.publication.handleException(
            self.object, self.request, sys.exc_info(), retry_allowed=False)
        self.request.response.outputBody()
        self.assertEqual(self.out.getvalue(), view_text)

    def testNoViewOnClassicClassException(self):
        from zope.interface import Interface
        from types import ClassType
        class ClassicError:
            __metaclass__ = ClassType
        class IClassicError(Interface):
            pass
        classImplements(ClassicError, IClassicError)
        s = zapi.getGlobalService(zapi.servicenames.Presentation)
        s.setDefaultViewName(IClassicError, self.presentation_type, 'name')
        view_text = 'You made a classic error ;-)'
        s.provideView(IClassicError, 'name', self.presentation_type,
                      [lambda obj,request: lambda: view_text])
        try:
            raise ClassicError
        except:
            pass
        self.publication.handleException(
            self.object, self.request, sys.exc_info(), retry_allowed=False)
        self.request.response.outputBody()
        # check we don't get the view we registered
        self.failIf(self.out.getvalue() == view_text)
        # check we do actually get something
        self.failIf(self.out.getvalue() == '')

    def testExceptionSideEffects(self):
        from zope.publisher.interfaces import IExceptionSideEffects
        class SideEffects(object):
            implements(IExceptionSideEffects)
            def __init__(self, exception):
                self.exception = exception
            def __call__(self, obj, request, exc_info):
                self.obj = obj
                self.request = request
                self.exception_type = exc_info[0]
                self.exception_from_info = exc_info[1]
        class SideEffectsFactory:
            def __call__(self, exception):
                self.adapter = SideEffects(exception)
                return self.adapter
        factory = SideEffectsFactory()
        from ZODB.POSException import ConflictError
        from zope.interface import Interface
        class IConflictError(Interface):
            pass
        classImplements(ConflictError, IConflictError)
        ztapi.provideAdapter(IConflictError, IExceptionSideEffects, factory)
        exception = ConflictError()
        try:
            raise exception
        except:
            pass
        self.publication.handleException(
            self.object, self.request, sys.exc_info(), retry_allowed=False)
        adapter = factory.adapter
        self.assertEqual(exception, adapter.exception)
        self.assertEqual(exception, adapter.exception_from_info)
        self.assertEqual(ConflictError, adapter.exception_type)
        self.assertEqual(self.object, adapter.obj)
        self.assertEqual(self.request, adapter.request)

    def testExceptionResetsResponse(self):
        self.request._response = BrowserResponse(
            self.request.response._outstream)
        self.request.response.setHeader('Content-Type', 'application/pdf')
        self.request.response.setCookie('spam', 'eggs')
        from ZODB.POSException import ConflictError
        try:
            raise ConflictError
        except:
            pass
        self.publication.handleException(
            self.object, self.request, sys.exc_info(), retry_allowed=False)
        self.request.response.outputBody()
        self.assertEqual(self.request.response.getHeader('Content-Type'),
                         'text/html;charset=utf-8')
        self.assertEqual(self.request.response._cookies, {})

    def testAbortOrCommitTransaction(self):
        txn = transaction.get()
        try:
            raise Exception
        except:
            pass
        self.publication.handleException(
            self.object, self.request, sys.exc_info(), retry_allowed=False)
        # assert that we get a new transaction
        self.assert_(txn is not transaction.get())    

    def testAbortTransactionWithErrorLoggingService(self):
        # provide our fake error logging service
        sm = getGlobalServices()
        sm.defineService(ErrorLogging, IErrorReportingService)
        sm.provideService(ErrorLogging, ErrorLoggingService())

        class FooError(Exception):
            pass

        last_txn_info = self.db.undoInfo()[0]
        try:
            raise FooError
        except FooError:
            pass
        self.publication.handleException(
            self.object, self.request, sys.exc_info(), retry_allowed=False)

        # assert that the last transaction is NOT our transaction
        new_txn_info = self.db.undoInfo()[0]
        self.assertEqual(last_txn_info, new_txn_info)

        # instead, we expect a message in our logging service
        error_log = sm.getService(ErrorLogging)
        self.assertEqual(len(error_log.exceptions), 1)
        error_info, request = error_log.exceptions[0]
        self.assertEqual(error_info[0], FooError)
        self.assert_(isinstance(error_info[1], FooError))
        self.assert_(request is self.request)

class ZopePublicationTests(BasePublicationTests):

    def testPlacefulAuth(self):
        principalRegistry.defineDefaultPrincipal('anonymous', '')

        root = self.db.open().root()
        app = root[ZopePublication.root_name]
        app['f1'] = Folder()
        f1 = app['f1']
        f1['f2'] = Folder()
        f1.setSiteManager(ServiceManager(AuthService1()))
        f2 = f1['f2']
        f2.setSiteManager(ServiceManager(AuthService2()))
        transaction.commit()

        from zope.app.container.interfaces import ISimpleReadContainer
        from zope.app.container.traversal import ContainerTraverser

        s = zapi.getGlobalService(zapi.servicenames.Presentation) 
        s.provideView(ISimpleReadContainer, '', IRequest,
                      ContainerTraverser, providing=IPublishTraverse)

        from zope.app.folder.interfaces import IFolder
        from zope.security.checker import defineChecker, InterfaceChecker
        defineChecker(Folder, InterfaceChecker(IFolder))

        self.publication.beforeTraversal(self.request)
        self.assertEqual(list(queryInteraction().participations),
                         [self.request])
        self.assertEqual(self.request.principal.id, 'anonymous')
        root = self.publication.getApplication(self.request)
        self.publication.callTraversalHooks(self.request, root)
        self.assertEqual(self.request.principal.id, 'anonymous')
        ob = self.publication.traverseName(self.request, root, 'f1')
        self.publication.callTraversalHooks(self.request, ob)
        self.assertEqual(self.request.principal.id, 'test.anonymous')
        ob = self.publication.traverseName(self.request, ob, 'f2')
        self.publication.afterTraversal(self.request, ob)
        self.assertEqual(self.request.principal.id, 'test.bob')
        self.assertEqual(list(queryInteraction().participations),
                         [self.request])
        self.publication.endRequest(self.request, ob)
        self.assertEqual(queryInteraction(), None)        

    def testTransactionCommitAfterCall(self):
        root = self.db.open().root()
        txn = transaction.get()
        # we just need a change in the database to make the
        # transaction notable in the undo log
        root['foo'] = object()
        last_txn_info = self.db.undoInfo()[0]
        self.publication.afterCall(self.request, self.object)
        self.assert_(txn is not transaction.get())
        new_txn_info = self.db.undoInfo()[0]
        self.failIfEqual(last_txn_info, new_txn_info)

    def testTransactionAnnotation(self):
        from zope.interface import directlyProvides
        from zope.app.location.traversing import LocationPhysicallyLocatable
        from zope.app.location.interfaces import ILocation
        from zope.app.traversing.interfaces import IPhysicallyLocatable
        from zope.app.traversing.interfaces import IContainmentRoot
        ztapi.provideAdapter(ILocation, IPhysicallyLocatable,
                             LocationPhysicallyLocatable)

        root = self.db.open().root()
        root['foo'] = foo = LocatableObject()
        root['bar'] = bar = LocatableObject()
        bar.__name__ = 'bar'
        foo.__name__ = 'foo'
        bar.__parent__ = foo
        foo.__parent__ = root
        directlyProvides(root, IContainmentRoot)

        from zope.publisher.interfaces import IRequest
        expected_path = "/foo/bar"
        expected_user = "/ " + self.user.id
        expected_request = IRequest.__module__ + '.' + IRequest.getName()

        self.publication.afterCall(self.request, bar)
        txn_info = self.db.undoInfo()[0]
        self.assertEqual(txn_info['location'], expected_path)
        self.assertEqual(txn_info['user_name'], expected_user)
        self.assertEqual(txn_info['request_type'], expected_request)

        # also, assert that we still get the right location when
        # passing an instance method as object.
        self.publication.afterCall(self.request, bar.foo)
        self.assertEqual(txn_info['location'], expected_path)

    def testSiteEvents(self):
        from zope.app.publication.interfaces import IBeforeTraverseEvent
        from zope.app.publication.interfaces import IEndRequestEvent

        set = []
        clear = []
        ztapi.handle([IBeforeTraverseEvent], set.append)
        ztapi.handle([IEndRequestEvent], clear.append)

        ob = object()

        # This should fire the BeforeTraverseEvent
        self.publication.callTraversalHooks(self.request, ob)

        self.assertEqual(len(set), 1)
        self.assertEqual(len(clear), 0)
        self.assertEqual(set[0].object, ob)

        ob2 = object()

        # This should fire the EndRequestEvent
        self.publication.endRequest(self.request, ob2)

        self.assertEqual(len(set), 1)
        self.assertEqual(len(clear), 1)
        self.assertEqual(clear[0].object, ob2)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ZopePublicationTests),
        unittest.makeSuite(ZopePublicationErrorHandling),
        ))

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
