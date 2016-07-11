import zope.app.publication.tests as tests
import tests.test_browserpublication
import tests.test_dependencies
import tests.test_functional
import tests.test_http
import tests.test_httpfactory
import tests.test_proxycontrol
import tests.test_requestpublicationfactories
import tests.test_requestpublicationregistry
import tests.test_simplecomponenttraverser
import tests.test_xmlrpcpublication
import tests.test_zopepublication
import unittest


def collect_tests():
    """Combine all test suites to have one entry point."""
    return unittest.TestSuite((
        tests.test_browserpublication.test_suite(),
        tests.test_dependencies.test_suite(),
        tests.test_functional.test_suite(),
        tests.test_http.test_suite(),
        tests.test_httpfactory.test_suite(),
        tests.test_proxycontrol.test_suite(),
        tests.test_requestpublicationfactories.test_suite(),
        tests.test_simplecomponenttraverser.test_suite(),
        tests.test_xmlrpcpublication.test_suite(),
        tests.test_zopepublication.test_suite(),
    ))
