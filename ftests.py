##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Functional tests for Zope Publication

$Id: ftests.py 25177 2004-06-02 13:17:31Z jim $
"""
import unittest
from zope.app import zapi
from zope.app.tests.functional import BrowserTestCase

class TestErrorReportingService(BrowserTestCase):

    def testAddMissingErrorReportingService(self):
        # Unregister and remove the existing error reporting service
        self.publish(
            '/++etc++site/default/RegistrationManager/ServiceRegistration/',
            basic='mgr:mgrpw',
            form={'field.permission': '',
                  'field.status': 'Unregistered',
                  'UPDATE_SUBMIT': 'Change'})
        self.publish(
            '/++etc++site/default/RegistrationManager/',
            basic='mgr:mgrpw',
            form={'keys': ['ServiceRegistration'],
                  'remove_submit': 'Remove'})
        self.publish(
            '/++etc++site/default/@@contents.html',
            basic='mgr:mgrpw',
            form={'ids': ['ErrorLogging'],
                  'container_delete_button': 'Delete'})

        root = self.getRootFolder()
        default = zapi.traverse(root, '++etc++site/default')
        self.assert_('ErrorLogging' not in default.keys())

        # Force a NotFoundError, so that the error reporting service is
        # created again.
        response = self.publish('/foobar', basic='mgr:mgrpw',
                                handle_errors=True)
        self.assertEqual(response.getStatus(), 404)
        body = response.getBody()
        self.assert_(
            'The page that you are trying to access is not available' in body)

        # Now make sure that we have a new error reporting service with the
        # right entry.
        root = self.getRootFolder()
        default = zapi.traverse(root, '++etc++site/default')
        self.assert_('ErrorLogging' in default.keys())
        entry = default['ErrorLogging'].getLogEntries()[0]
        self.assertEqual(entry['type'], 'NotFound')
        self.assert_('foobar' in entry['tb_text'])


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestErrorReportingService),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
