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

from zope.interface import Interface

from zope.component import getService, getServiceManager

from zope.publisher.publish import publish
from zope.publisher.browser import TestRequest
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.interfaces.browser import IBrowserPresentation

from zope.proxy.context import getWrapperContext, wrapperTypes
from zope.proxy.introspection import removeAllProxies

from zope.security.checker import defineChecker, NamesChecker

from zope.app.security.registries.principalregistry import principalRegistry
from zope.app.security.grants.principalrolemanager \
     import principalRoleManager

from zope.app.publication.zopepublication import ZopePublication
from zope.app.publication.browser import BrowserPublication
from zope.app.publication.traversers import TestTraverser
from zope.app.publication.tests.test_zopepublication \
     import BasePublicationTests as BasePublicationTests_


def foo():
    " "
    return '<html><body>hello base fans</body></html>'

class DummyPublished:

    __implements__ = IBrowserPublisher

    def publishTraverse(self, request, name):
        if name == 'bruce':
            return foo
        raise KeyError, name

    def browserDefault(self, request):
        return self, ['bruce']

class DummyView(DummyPublished, BrowserView):

    __implements__ = DummyPublished.__implements__, BrowserView.__implements__


class BasePublicationTests(BasePublicationTests_):

    def _createRequest(self, path, publication, **kw):
        request = TestRequest(PATH_INFO=path, **kw)
        request.setPublication(publication)
        return request


class BrowserDefaultTests(BasePublicationTests):
    """
    test browser default

    many views lead to a default view
    <base href="/somepath/@@view/view_method">

    """
    klass = BrowserPublication

    def testBaseTagNoBase(self):
        self._testBaseTags('/somepath/@@view/', '')

    def testBaseTag1(self):
        self._testBaseTags('/somepath/@@view',
                           'http://127.0.0.1/somepath/@@view/bruce')

    def testBaseTag2(self):
        self._testBaseTags('/somepath/',
                           'http://127.0.0.1/somepath/@@view/bruce')

    def testBaseTag3(self):
        self._testBaseTags('/somepath',
                           'http://127.0.0.1/somepath/@@view/bruce')



    def _testBaseTags(self, url, expected):

        class I1(Interface): pass

        from persistence import Persistent

        class O1(Persistent):
            __implements__ = I1


        pub = BrowserPublication(self.db)

        getService(None,'Views').provideView(I1, 'view',
                           IBrowserPresentation, [DummyView])
        getService(None,'Views').setDefaultViewName(I1,
                             IBrowserPresentation, 'view')
        getService(None, 'Views').provideView(None,
                    '_traverse', IBrowserPresentation, [TestTraverser])

        ob = O1()

        ## the following is for running the tests standalone
        principalRegistry.defineDefaultPrincipal(
            'tim', 'timbot', 'ai at its best')

        principalRoleManager.assignRoleToPrincipal('Manager', 'tim')


        # now place our object inside the application
        from transaction import get_transaction

        connection = self.db.open()
        app = connection.root()['Application']
        app.somepath = ob
        get_transaction().commit()
        connection.close()

        defineChecker(app.__class__, NamesChecker(somepath='xxx'))

        req = self._createRequest(url, pub)
        response = req.response

        publish(req, handle_errors=0)

        self.assertEqual(response.getBase(), expected)


    def _createRequest(self, path, publication, **kw):
        request = TestRequest(PATH_INFO=path, **kw)
        request.setPublication(publication)
        return request



class SimpleObject:
    def __init__(self, v):
        self.v = v

class I1(Interface):
    pass

class mydict(dict):
    __implements__ = I1


class BrowserPublicationTests(BasePublicationTests):

    klass = BrowserPublication

    def testNativeTraverseNameWrapping(self):
        pub = self.klass(self.db)
        ob = DummyPublished()
        ob2 = pub.traverseName(self._createRequest('/bruce',pub), ob, 'bruce')
        self.failUnless(ob2 is not ob)
        self.failUnless(type(ob2) in wrapperTypes)

    def testAdaptedTraverseNameWrapping(self):

        class Adapter:
            " "
            __implements__ = IBrowserPublisher
            def __init__(self, context, request):
                self.context = context
                self.counter = 0

            def publishTraverse(self, request, name):
                self.counter+=1
                return self.context[name]

        provideView=getService(None, "Views").provideView
        provideView(I1, '_traverse', IBrowserPresentation, [Adapter])
        ob = mydict()
        ob['bruce'] =  SimpleObject('bruce')
        ob['bruce2'] =  SimpleObject('bruce2')
        pub = self.klass(self.db)
        ob2 = pub.traverseName(self._createRequest('/bruce',pub), ob, 'bruce')
        self.failUnless(type(ob2) in wrapperTypes)
        unw = removeAllProxies(ob2)
        self.assertEqual(unw.v, 'bruce')

    def testAdaptedTraverseDefaultWrapping(self):
        # Test default content and make sure that it's wrapped.
        class Adapter:
            __implements__ = IBrowserPublisher
            def __init__(self, context, request):
                self.context = context

            def browserDefault(self, request):
                return (self.context['bruce'], 'dummy')

        provideView=getService(None, "Views").provideView
        provideView(I1, '_traverse', IBrowserPresentation, [Adapter])
        ob = mydict()
        ob['bruce'] =  SimpleObject('bruce')
        ob['bruce2'] =  SimpleObject('bruce2')
        pub = self.klass(self.db)
        ob2, x = pub.getDefaultTraversal(self._createRequest('/bruce',pub), ob)
        self.assertEqual(x, 'dummy')
        self.failUnless(type(ob2) in wrapperTypes)
        unw = removeAllProxies(ob2)
        self.assertEqual(unw.v, 'bruce')


    # XXX we no longer support path parameters! (At least for now)
    def XXXtestTraverseSkinExtraction(self):
        class I1(Interface): pass
        class C: __implements__ = I1
        class BobView(DummyView): pass

        pub = self.klass(self.db)
        ob = C()
        provideView=getService(None, "Views").provideView
        provideView(I1, 'edit', IBrowserPresentation, [BobView])

        r = self._createRequest('/@@edit;skin=zmi',pub)
        ob2 = pub.traverseName(r , ob, '@@edit;skin=zmi')
        self.assertEqual(r.getPresentationSkin(), 'zmi')
        self.assertEqual(ob2.__class__ , BobView)

        r = self._createRequest('/@@edit;skin=zmi',pub)
        ob2 = pub.traverseName(r , ob, '@@edit;skin=zmi')
        self.assertEqual(r.getPresentationSkin(), 'zmi')
        self.assertEqual(ob2.__class__ , BobView)

    def testTraverseName(self):
        pub = self.klass(self.db)
        class C:
            x = SimpleObject(1)
        ob = C()
        r = self._createRequest('/x',pub)
        provideView=getService(None, "Views").provideView
        provideView(None, '_traverse', IBrowserPresentation, [TestTraverser])
        ob2 = pub.traverseName(r, ob, 'x')
        self.assertEqual(removeAllProxies(ob2).v, 1)
        self.assertEqual(getWrapperContext(ob2), ob)

    def testTraverseNameView(self):
        pub = self.klass(self.db)
        class I(Interface): pass
        class C:
            __implements__ = I
        ob = C()
        class V:
            def __init__(self, context, request): pass
            __implements__ = IBrowserPresentation
        r = self._createRequest('/@@spam',pub)
        provideView=getService(None, "Views").provideView
        provideView(I, 'spam', IBrowserPresentation, [V])
        ob2 = pub.traverseName(r, ob, '@@spam')
        self.assertEqual(removeAllProxies(ob2).__class__, V)
        self.assertEqual(getWrapperContext(ob2), ob)

    def testTraverseNameServices(self):
        pub = self.klass(self.db)
        class C:
            def getServiceManager(self):
                return SimpleObject(1)
        ob = C()
        r = self._createRequest('/++etc++Services',pub)
        ob2 = pub.traverseName(r, ob, '++etc++Services')
        self.assertEqual(removeAllProxies(ob2).v, 1)
        self.assertEqual(getWrapperContext(ob2), ob)

    def testTraverseNameApplicationControl(self):
        from zope.app.applicationcontrol.applicationcontrol \
             import applicationController, applicationControllerRoot
        pub = self.klass(self.db)
        r = self._createRequest('/++etc++ApplicationController',pub)
        ac = pub.traverseName(r,
                              applicationControllerRoot,
                              '++etc++ApplicationController')
        self.assertEqual(ac, applicationController)
        r = self._createRequest('/++etc++ApplicationController',pub)
        app = r.publication.getApplication(r)
        self.assertEqual(app, applicationControllerRoot)


def test_suite():
    t2 = unittest.makeSuite(BrowserPublicationTests, 'test')
    t3 = unittest.makeSuite(BrowserDefaultTests, 'test')
    return unittest.TestSuite((t2, t3))


if __name__ == '__main__':
    unittest.TextTestRunner().run( test_suite() )
