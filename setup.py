##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Setup for zope.app.publication package

$Id$
"""

import os

from setuptools import setup, find_packages, Extension

setup(name='zope.app.publication',
      version='3.4dev',
      url='http://svn.zope.org/zope.app.publication',
      license='ZPL 2.1',
      description='Zope publication',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope', 'zope.app'],
      extras_require = dict(test=['zope.app.testing']),
      install_requires=['zope.interface',
                        'ZODB3',
                        'zope.component',
                        'zope.i18n',
                        'zope.app.http',
                        'zope.app.applicationcontrol',
                        'zope.app.error',
                        'zope.app.exception',
                        'zope.app.security'
                        ],
      include_package_data = True,
      zip_safe = False,
      )
