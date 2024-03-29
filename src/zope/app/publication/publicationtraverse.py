##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
import warnings

from zope.traversing.publicationtraverse import \
    PublicationTraverse  # noqa: F401 E501 (BBB and long line)
from zope.traversing.publicationtraverse import \
    PublicationTraverser  # noqa: F401 E501 (BBB and long line)


warnings.warn("""%s is deprecated

If you want PublicationTraverser, it's now in
zope.traversing.publicationtraverse.  Anything else that was here is
deprecated.
""" % __name__, DeprecationWarning, stacklevel=1)


# BBB: do not use
class DuplicateNamespaces(Exception):
    """More than one namespace was specified in a request"""


# BBB: do not use
class UnknownNamespace(Exception):
    """A parameter specified an unknown namespace"""
