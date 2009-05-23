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
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Default View Tests

$Id$
"""
from unittest import main
from zope.testing.doctestunit import DocTestSuite
from zope.component.testing import setUp, tearDown

def test_suite():
    return DocTestSuite('zope.app.publication.defaultview',
                        setUp=setUp, tearDown=tearDown)

if __name__ == '__main__':
    main(defaultTest='test_suite')
