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
"""HTTP Publication

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.app.publication.zopepublication import ZopePublication
from zope.component import getView
from zope.publisher.publish import mapply
from zope.app.http.interfaces import IHTTPException

class BaseHTTPPublication(ZopePublication):
    """Base for HTTP-based protocol publications"""

    def annotateTransaction(self, txn, request, ob):
        txn = super(BaseHTTPPublication, self).annotateTransaction(
            txn, request, ob)
        request_info = request.method + ' ' + request.getURL()
        txn.setExtendedInfo('request_info', request_info)
        return txn

class HTTPPublication(BaseHTTPPublication):
    """HTTP-specific publication"""

    def callObject(self, request, ob):
        # Exception handling, dont try to call request.method
        if not IHTTPException.providedBy(ob):
            ob = getView(ob, request.method, request)
            ob = getattr(ob, request.method)
        return mapply(ob, request.getPositionalArguments(), request)
