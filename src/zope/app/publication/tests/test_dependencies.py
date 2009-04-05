import os
import unittest

from zope.interface import implements
from zope.component import getMultiAdapter
from zope.app.testing import functional
from zope.publisher.browser import TestRequest

from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.app.publication.traversers import SimpleComponentTraverser

PublicationDependenciesLayer = functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftest_zcml_dependencies.zcml'),
    __name__, 'PublicationDependenciesLayer', allow_teardown=True)


class ZCMLDependencies(functional.BrowserTestCase):

    def test_zcml_can_load_with_only_zope_component_meta(self):
        # this is just an example.  It is supposed to show that the
        # configure.zcml file has loaded successfully.

        request = TestRequest()

        sample = object()
        res = getMultiAdapter(
            (sample, request), IBrowserPublisher)
        self.failUnless(isinstance(res, SimpleComponentTraverser))
        self.failUnless(res.context is sample)

def test_suite():
    suite = unittest.TestSuite()
    ZCMLDependencies.layer = PublicationDependenciesLayer
    suite.addTest(unittest.makeSuite(ZCMLDependencies))
    return suite


if __name__ == '__main__':
    unittest.main()
