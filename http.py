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

$Id: http.py,v 1.6 2004/03/05 22:09:13 jim Exp $
"""

from zope.app.publication.zopepublication import ZopePublication
from zope.component import getView
from zope.publisher.publish import mapply
from zope.app.interfaces.http import IHTTPException

class HTTPPublication(ZopePublication):
    "HTTP-specific support"

    def callObject(self, request, ob):
        # Exception handling, dont try to call request.method
        if not IHTTPException.providedBy(ob):
            ob = getView(ob, request.method, request)
            ob = getattr(ob, request.method)
        return mapply(ob, request.getPositionalArguments(), request)
