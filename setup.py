##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
# This package is developed by the Zope Toolkit project, documented here:
# http://docs.zope.org/zopetoolkit
# When developing and releasing this package, please follow the documented
# Zope Toolkit policies as described by this documentation.
##############################################################################

version = '3.12.0'

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.app.publication',
    version=version,
    author='Zope Corporation and Contributors',
    author_email='zope-dev@zope.org',
    description='Zope publication',
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license='ZPL 2.1',
    keywords = "zope publication",
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url='http://pypi.python.org/pypi/zope.app.publication',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['zope', 'zope.app'],
    extras_require = dict(
        test=['zope.annotation',
              'zope.app.appsetup >= 3.14.0',
              'zope.app.exception',
              'zope.app.http',
              'zope.app.wsgi >= 3.9.0',
              'zope.applicationcontrol>=3.5.0',
              'zope.browserpage',
              'zope.login',
              'zope.password',
              'zope.principalregistry',
              'zope.security',
              'zope.securitypolicy',
              'zope.site']),
    install_requires=['zope.interface',
                      'ZODB3',
                      'zope.authentication',
                      'zope.component',
                      'zope.error',
                      'zope.browser>=1.2',
                      'zope.location',
                      'zope.publisher>=3.12.4',
                      'zope.traversing>=3.9.0',
                      'setuptools',
                      ],
    include_package_data = True,
    zip_safe = False,
    )
