##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""

$Id: vfs.py,v 1.2 2002/12/25 14:13:08 jim Exp $
"""

from zope.app.publication.zopepublication import ZopePublication

from zope.component import queryView
from zope.publisher.interfaces import NotFound
from zope.publisher.publish import mapply


class VFSPublication(ZopePublication):
    """The Publication will do all the work for the VFS"""


    def callObject(self, request, ob):

        view = queryView(ob, 'vfs', request, self)
        #view = ob

        if view is not self:
            method = getattr(view, request.method)
        else:
            raise NotFound(ob, 'vfs', request)

        return mapply(method, request.getPositionalArguments(), request)
