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
import unittest
import sys

from zope.interface.verify import verifyClass
from zope.interface import implements, classImplements, implementedBy

from zodb.db import DB
from zodb.storage.mapping import MappingStorage

from zope.app.tests.placelesssetup import PlacelessSetup
from zope.component.adapter import provideAdapter
from zope.component.view import provideView, setDefaultViewName

from zope.i18n.interfaces import IUserPreferredCharsets

from zope.publisher.base import TestPublication
from zope.publisher.http import IHTTPRequest, HTTPCharsets

from zope.security import simplepolicies
from zope.security.management import setSecurityPolicy, getSecurityManager

from zope.app.security.registries.principalregistry import principalRegistry
from zope.app.interfaces.security import IUnauthenticatedPrincipal

from zope.app.publication.zopepublication import ZopePublication

from zope.app.content.folder import Folder, RootFolder

from zope.component.interfaces import IServiceService

from zope.publisher.base import TestRequest
from zope.publisher.browser import BrowserResponse

from zope.context import getWrapperContext

from transaction import get_transaction
from cStringIO import StringIO

from zope.app.services.servicenames import Authentication

class BasePublicationTests(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        provideAdapter(IHTTPRequest, IUserPreferredCharsets, HTTPCharsets)
        self.policy = setSecurityPolicy(
            simplepolicies.PermissiveSecurityPolicy()
            )
        self.db = DB(MappingStorage("foo"))

        connection = self.db.open()
        root = connection.root()
        app = getattr(root, ZopePublication.root_name, None)

        if app is None:
            from zope.app.content.folder import RootFolder

            app = RootFolder()
            root[ZopePublication.root_name] = app

            get_transaction().commit()

        connection.close()

        from zope.app.traversing.namespace import provideNamespaceHandler
        from zope.app.traversing.namespace import view, resource, etc
        provideNamespaceHandler('view', view)
        provideNamespaceHandler('resource', resource)
        provideNamespaceHandler('etc', etc)

    def tearDown(self):
        setSecurityPolicy(self.policy) # XXX still needed?
        PlacelessSetup.tearDown(self)

    def testInterfacesVerify(self):
        for interface in implementedBy(ZopePublication):
            verifyClass(interface, TestPublication)

class Principal:
    def __init__(self, id): self._id = id
    def getId(self): return self._id
    def getTitle(self): return ''
    def getDescription(self): return ''

class UnauthenticatedPrincipal(Principal):
    implements(IUnauthenticatedPrincipal)


class AuthService1:

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


class ServiceManager:

    implements(IServiceService) # a dirty lie

    def __init__(self, auth):
        self.auth = auth

    def queryService(self, name, default=None):
        if name == Authentication:
            return self.auth
        else:
            return default


class ZopePublicationErrorHandling(BasePublicationTests):

    def setUp(self):
        BasePublicationTests.setUp(self)
        root = self.db.open().root()
        self.out = StringIO()
        self.request = TestRequest('/f1/f2', outstream=self.out)
        from zope.interface import Interface
        self.presentation_type = Interface
        self.request._presentation_type = self.presentation_type
        self.publication = ZopePublication(self.db)
        self.object = object()  # doesn't matter what it is

    def testRetryAllowed(self):
        from zodb.interfaces import ConflictError
        from zope.publisher.interfaces import Retry
        try:
            raise ConflictError
        except:
            pass
        self.assertRaises(Retry, self.publication.handleException,
            self.object, self.request, sys.exc_info(), retry_allowed=True)

    def testRetryNotAllowed(self):
        from zodb.interfaces import ConflictError
        from zope.publisher.interfaces import Retry
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
        self.assertEqual(' '.join(value[9:]),
                         'in testRetryNotAllowed raise ConflictError'
                         ' ConflictError: database conflict error')

    def testViewOnException(self):
        from zodb.interfaces import ConflictError
        from zope.interface import Interface
        class IConflictError(Interface):
            pass
        classImplements(ConflictError, IConflictError)
        setDefaultViewName(IConflictError, self.presentation_type, 'name')
        view_text = 'You had a conflict error'
        provideView(IConflictError, 'name', self.presentation_type,
                    [lambda obj,request: lambda: view_text])
        try:
            raise ConflictError
        except:
            pass
        self.publication.handleException(
            self.object, self.request, sys.exc_info(), retry_allowed=False)
        self.request.response.outputBody()
        self.assertEqual(self.out.getvalue(), view_text)

    def testNoViewOnClassicClassException(self):
        from zodb.interfaces import ConflictError
        from zope.interface import Interface
        from types import ClassType
        class ClassicError:
            __metaclass__ = ClassType
        class IClassicError(Interface):
            pass
        classImplements(ClassicError, IClassicError)
        setDefaultViewName(IClassicError, self.presentation_type, 'name')
        view_text = 'You made a classic error ;-)'
        provideView(IClassicError, 'name', self.presentation_type,
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
        class SideEffects:
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
        from zodb.interfaces import ConflictError
        from zope.interface import Interface
        class IConflictError(Interface):
            pass
        classImplements(ConflictError, IConflictError)
        provideAdapter(IConflictError, IExceptionSideEffects, factory)
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
        self.request._response = BrowserResponse(self.request.response._outstream)
        self.request.response.setHeader('Content-Type', 'application/pdf')
        self.request.response.setCookie('spam', 'eggs')
        from zodb.interfaces import ConflictError
        try:
            raise ConflictError
        except:
            pass
        self.publication.handleException(
            self.object, self.request, sys.exc_info(), retry_allowed=False)
        self.request.response.outputBody()
        self.assertEqual(self.request.response.getHeader('Content-Type'), 'text/html')
        self.assertEqual(self.request.response._cookies, {})


class ZopePublicationTests(BasePublicationTests):

    def testPlacefulAuth(self):
        principalRegistry.defineDefaultPrincipal('anonymous', '')

        root = self.db.open().root()
        app = root[ZopePublication.root_name]
        app.setObject('f1', Folder())
        f1 = app['f1']
        f1.setObject('f2', Folder())
        f1.setSiteManager(ServiceManager(AuthService1()))
        f2 = f1['f2']
        f2.setSiteManager(ServiceManager(AuthService2()))
        get_transaction().commit()

        request = TestRequest('/f1/f2')

        from zope.component.view import provideView
        from zope.app.interfaces.container import ISimpleReadContainer
        from zope.app.container.traversal import ContainerTraverser
        from zope.component.interfaces import IPresentation
        provideView(ISimpleReadContainer, '_traverse', IPresentation,
                    ContainerTraverser)

        from zope.app.interfaces.content.folder import IFolder
        from zope.security.checker import defineChecker, InterfaceChecker
        defineChecker(Folder, InterfaceChecker(IFolder))
        defineChecker(RootFolder, InterfaceChecker(IFolder))

        request.setViewType(IPresentation)

        publication = ZopePublication(self.db)

        publication.beforeTraversal(request)
        user = getSecurityManager().getPrincipal()
        self.assertEqual(user, request.user)
        self.assertEqual(getWrapperContext(user), principalRegistry)
        self.assertEqual(request.user.getId(), 'anonymous')
        self.assertEqual(getWrapperContext(request.user), principalRegistry)
        root = publication.getApplication(request)
        publication.callTraversalHooks(request, root)
        self.assertEqual(request.user.getId(), 'anonymous')
        ob = publication.traverseName(request, root, 'f1')
        publication.callTraversalHooks(request, ob)
        self.assertEqual(request.user.getId(), 'test.anonymous')
        self.assertEqual(getWrapperContext(request.user).__class__,
                         AuthService1)
        ob = publication.traverseName(request, ob, 'f2')
        publication.afterTraversal(request, ob)
        self.assertEqual(request.user.getId(), 'test.bob')
        self.assertEqual(getWrapperContext(request.user).__class__,
                         AuthService2)
        user = getSecurityManager().getPrincipal()
        self.assertEqual(user, request.user)
        self.assertEqual(getWrapperContext(user).__class__, AuthService2)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ZopePublicationTests),
        unittest.makeSuite(ZopePublicationErrorHandling),
        ))

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
