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

from zope.interface.verify import verifyClass
from zope.interface.implements import instancesOfObjectImplements

from zodb.storage.mapping import DB

from zope.app.tests.placelesssetup import PlacelessSetup
from zope.component.adapter import provideAdapter

from zope.i18n.interfaces import IUserPreferredCharsets

from zope.publisher.base import TestPublication
from zope.publisher.http import IHTTPRequest, HTTPCharsets

from zope.security import simplesecuritypolicies
from zope.security.securitymanagement import setSecurityPolicy

from zope.app.security.registries.principalregistry import principalRegistry
from zope.app.interfaces.security import IUnauthenticatedPrincipal

from zope.app.publication.zopepublication import ZopePublication

from zope.app.content.folder import Folder, RootFolder

from zope.component.interfaces import IServiceService

from zope.publisher.base import TestRequest

from zope.component.service import serviceManager

from transaction import get_transaction

class BasePublicationTests(PlacelessSetup, unittest.TestCase):
    klass = ZopePublication

    def setUp(self):
        PlacelessSetup.setUp(self)
        provideAdapter(IHTTPRequest, IUserPreferredCharsets, HTTPCharsets)
        self.policy = setSecurityPolicy(
            simplesecuritypolicies.PermissiveSecurityPolicy()
            )
        self.db = DB("foo")

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
        for interface in instancesOfObjectImplements(self.klass):
            verifyClass(interface, TestPublication)

class Principal:
    def __init__(self, id): self._id = id
    def getId(self): return self._id
    def getTitle(self): return ''
    def getDescription(self): return ''

class UnauthenticatedPrincipal(Principal):
    __implements__ = IUnauthenticatedPrincipal


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

    __implements__ = IServiceService # a dirty lie

    def __init__(self, auth):   self.auth = auth
    def get(self, key, d=None):      return self.auth
    __getitem__ = get
    def __contains__(self, key): return 1

    def getService(self, name):
        # I just wanna get the test to pass. Waaaaa
        return serviceManager.getService(name)


class ZopePublicationTests(BasePublicationTests):
    klass = ZopePublication

    def testPlacefulAuth(self):
        principalRegistry.defineDefaultPrincipal('anonymous', '')

        root = self.db.open().root()
        app = root[ZopePublication.root_name]
        app.setObject('f1', Folder())
        f1 = app['f1']
        f1.setObject('f2', Folder())
        f1.setServiceManager(ServiceManager(AuthService1()))
        f2 = f1['f2']
        f2.setServiceManager(ServiceManager(AuthService2()))
        get_transaction().commit()

        request = TestRequest('/f1/f2')

        from zope.component.view import provideView
        from zope.app.interfaces.container import ISimpleReadContainer
        from zope.app.container.traversal \
             import ContainerTraverser
        from zope.component.interfaces import IPresentation
        provideView(ISimpleReadContainer, '_traverse', IPresentation,
                    ContainerTraverser)

        from zope.app.interfaces.content.folder import IFolder
        from zope.security.checker import defineChecker, InterfaceChecker
        defineChecker(Folder, InterfaceChecker(IFolder))
        defineChecker(RootFolder, InterfaceChecker(IFolder))

        request.setViewType(IPresentation)

        publication = self.klass(self.db)

        publication.beforeTraversal(request)
        self.assertEqual(request.user.getId(), 'anonymous')
        root = publication.getApplication(request)
        publication.callTraversalHooks(request, root)
        self.assertEqual(request.user.getId(), 'anonymous')
        ob = publication.traverseName(request, root, 'f1')
        publication.callTraversalHooks(request, ob)
        self.assertEqual(request.user.getId(), 'test.anonymous')
        ob = publication.traverseName(request, ob, 'f2')
        publication.afterTraversal(request, ob)
        self.assertEqual(request.user.getId(), 'test.bob')

def test_suite():
    return unittest.makeSuite(ZopePublicationTests)

if __name__ == '__main__':
    unittest.TextTestRunner().run( test_suite() )
