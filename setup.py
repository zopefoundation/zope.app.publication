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
# https://zopetoolkit.readthedocs.io/
# When developing and releasing this package, please follow the documented
# Zope Toolkit policies as described by this documentation.
##############################################################################
import os

from setuptools import setup


def read(*rnames):
    with open(os.path.join(os.path.dirname(__file__), *rnames)) as f:
        return f.read()


TEST_REQUIREMENTS = [
    'zope.annotation',
    'zope.app.appsetup >= 3.14.0',
    'zope.app.http >= 4.0',
    'zope.app.wsgi[testlayer] >= 4.3',
    'zope.applicationcontrol>=4.0.0a1',
    'zope.browserpage',
    'zope.login',
    'zope.password',
    'zope.principalregistry',
    'zope.securitypolicy',
    'zope.site>=4.0.0a1',
    'zope.testing',
    'zope.testrunner >= 6.4',
    'ZODB >= 5.1',
]

setup(
    name='zope.app.publication',
    version='6.0',
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.dev',
    description='Zope publication',
    long_description=(
        read('README.rst') +
        '\n\n' +
        read('CHANGES.rst')
    ),
    license='ZPL-2.1',
    keywords="zope publication",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope :: 3',
    ],
    url='https://pypi.org/project/zope.app.publication/',
    extras_require=dict(test=TEST_REQUIREMENTS),
    python_requires='>=3.9',
    install_requires=[
        'zope.interface',
        'zope.authentication',
        'zope.component',
        'zope.error',
        'zope.browser>=1.2',
        'zope.location',
        'zope.publisher>=4.0.0a2',
        'zope.traversing>=4.0.0a2',
        'zope.i18n>=4.0.0a3',
        'transaction>=1.1.0',
        'setuptools',
    ],
    include_package_data=True,
    zip_safe=False,
)
