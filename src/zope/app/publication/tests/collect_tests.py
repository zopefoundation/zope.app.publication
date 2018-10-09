from __future__ import absolute_import

from . import test_browserpublication
from . import test_dependencies
from . import test_functional
from . import test_http
from . import test_httpfactory
from . import test_proxycontrol
from . import test_requestpublicationfactories
from . import test_requestpublicationregistry
from . import test_simplecomponenttraverser
from . import test_xmlrpcpublication
from . import test_zopepublication
import unittest


def collect_tests():
    """Combine all test suites to have one entry point."""
    return unittest.TestSuite((
        test_browserpublication.test_suite(),
        test_dependencies.test_suite(),
        test_functional.test_suite(),
        test_http.test_suite(),
        test_httpfactory.test_suite(),
        test_proxycontrol.test_suite(),
        test_requestpublicationfactories.test_suite(),
        test_simplecomponenttraverser.test_suite(),
        test_xmlrpcpublication.test_suite(),
        test_zopepublication.test_suite(),
    ))
