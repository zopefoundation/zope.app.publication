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

import warnings

warnings.warn("""zope.app.publicationtraverse is deprecated

If you want PublicationTraverser, it's now in
zope.traversing.publicationtraverse.  Anything else that was here is
deprecated.
""", DeprecationWarning, stacklevel=1)


from zope.traversing.publicationtraverse import PublicationTraverse #BBB import
from zope.traversing.publicationtraverse import PublicationTraverser #BBB import

#BBB: do not use
class DuplicateNamespaces(Exception):
    """More than one namespace was specified in a request"""

#BBB: do not use
class UnknownNamespace(Exception):
    """A parameter specified an unknown namespace"""

