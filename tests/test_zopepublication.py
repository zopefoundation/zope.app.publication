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
"""Zope Publication Tests

$Id: test_zopepublication.py,v 1.25 2004/03/08 12:05:59 srichter Exp $
"""
import unittest
import sys
from cStringIO import StringIO

from ZODB.tests.util import DB

from zope.interface.verify import verifyClass
from zope.interface import implements, classImplements, implementedBy
from zope.i18n.interfaces import IUserPreferredCharsets
from zope.component.interfaces import IServiceService
from zope.publisher.base import TestPublication
from zope.publisher.http import IHTTPRequest, HTTPCharsets
from zope.publisher.interfaces import IRequest
from zope.security import simplepolicies
from zope.security.management import setSecurityPolicy, getSecurityManager

from zope.app import zapi
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.tests import ztapi

from zope.app.services.servicenames import Authentication
from zope.app.security.principalregistry import principalRegistry
from zope.app.security.interfaces import IUnauthenticatedPrincipal, IPrincipal
from zope.app.publication.zopepublication import ZopePublication
from zope.app.folder import Folder, rootFolder
from zope.publisher.base import TestRequest
from zope.publisher.browser import BrowserResponse

class BasePublicationTests(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(BasePublicationTests, self).setUp()
        ztapi.provideAdapter(IHTTPRequest, IUserPreferredCharsets,
                             HTTPCharsets)
        self.policy = setSecurityPolicy(
            simplepolicies.PermissiveSecurityPolicy()
            )
        self.db = DB()

        connection = self.db.open()
        root = connection.root()
        app = getattr(root, ZopePublication.root_name, None)

        if app is None:
            from zope.app.folder import rootFolder
            app = rootFolder()
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
    implements(IPrincipal)
    def __init__(self, id):
        self.id = id
        self.title = ''
        self.description = ''

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
        self.out = StringIO()
        self.request = TestRequest('/f1/f2', outstream=self.out)
        from zope.interface import Interface
        self.presentation_type = Interface
        self.request._presentation_type = self.presentation_type
        self.publication = ZopePublication(self.db)
        self.object = object()  # doesn't matter what it is

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
        self.assertEqual(' '.join(value[9:]),
                         'in testRetryNotAllowed raise ConflictError'
                         ' ConflictError: database conflict error')

    def testViewOnException(self):
        from ZODB.POSException import ConflictError
        from zope.interface import Interface
        class IConflictError(Interface):
            pass
        classImplements(ConflictError, IConflictError)
        s = zapi.getService(None, zapi.servicenames.Presentation)
        s.setDefaultViewName(IConflictError,
                             self.presentation_type, 'name')
        view_text = 'You had a conflict error'
        s = zapi.getService(None, zapi.servicenames.Presentation) 
        s.provideView(IConflictError, 'name', self.presentation_type,
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
        from zope.interface import Interface
        from types import ClassType
        class ClassicError:
            __metaclass__ = ClassType
        class IClassicError(Interface):
            pass
        classImplements(ClassicError, IClassicError)
        s = zapi.getService(None, zapi.servicenames.Presentation)
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
        self.request._response = BrowserResponse(self.request.response._outstream)
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
        self.assertEqual(self.request.response.getHeader('Content-Type'), 'text/html')
        self.assertEqual(self.request.response._cookies, {})


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
        get_transaction().commit()

        request = TestRequest('/f1/f2')

        from zope.app.container.interfaces import ISimpleReadContainer
        from zope.app.container.traversal import ContainerTraverser

        s = zapi.getService(None, zapi.servicenames.Presentation) 
        s.provideView(ISimpleReadContainer, '_traverse', IRequest,
                      ContainerTraverser)

        from zope.app.folder.interfaces import IFolder
        from zope.security.checker import defineChecker, InterfaceChecker
        defineChecker(Folder, InterfaceChecker(IFolder))

        publication = ZopePublication(self.db)

        publication.beforeTraversal(request)
        user = getSecurityManager().getPrincipal()
        self.assertEqual(user, request.user)
        self.assertEqual(request.user.id, 'anonymous')
        root = publication.getApplication(request)
        publication.callTraversalHooks(request, root)
        self.assertEqual(request.user.id, 'anonymous')
        ob = publication.traverseName(request, root, 'f1')
        publication.callTraversalHooks(request, ob)
        self.assertEqual(request.user.id, 'test.anonymous')
        ob = publication.traverseName(request, ob, 'f2')
        publication.afterTraversal(request, ob)
        self.assertEqual(request.user.id, 'test.bob')
        user = getSecurityManager().getPrincipal()
        self.assertEqual(user, request.user)
        

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ZopePublicationTests),
        unittest.makeSuite(ZopePublicationErrorHandling),
        ))

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
