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

$Id: http.py,v 1.5 2003/03/29 17:08:08 sidnei Exp $
"""

from zope.app.publication.zopepublication import ZopePublication
from zope.component import getView
from zope.publisher.publish import mapply
from zope.app.interfaces.http import IHTTPException

class HTTPPublication(ZopePublication):
    "HTTP-specific support"

    def callObject(self, request, ob):
        # Exception handling, dont try to call request.method
        if not IHTTPException.isImplementedBy(ob):
            ob = getView(ob, request.method, request)
            ob = getattr(ob, request.method)
        return mapply(ob, request.getPositionalArguments(), request)
