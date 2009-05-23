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
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Backwards compatibility: moved this module to
`zope.traversing.publicationtraverse`.

$Id$
"""
__docformat__ = 'restructuredtext'

import zope.deferredimport

zope.deferredimport.deprecatedFrom(
    "This module has moved to zope.traversing. This import will stop "
    "working in the future.",
    'zope.traversing.publicationtraverse',
    'DuplicateNamespaces',
    'UnknownNamespace',
    'PublicationTraverse',
    'PublicationTraverser',
    )
