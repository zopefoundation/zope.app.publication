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
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id: http.py,v 1.3 2003/02/07 15:59:41 jim Exp $
"""

from zope.app.publication.zopepublication import ZopePublication
from zope.component import getView
from zope.publisher.publish import mapply

class HTTPPublication(ZopePublication):
    "HTTP-specific support"

    def callObject(self, request, ob):
        ob = getView(ob, request.method, request)
        ob = getattr(ob, request.method)
        return mapply(ob, request.getPositionalArguments(), request)
