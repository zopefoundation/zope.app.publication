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
"""XML-RPC Publication Handler.

This module specifically implements a custom nameTraverse() method.

$Id: xmlrpc.py,v 1.7 2003/08/04 23:19:04 srichter Exp $
"""
from zope.app.context import ContextWrapper
from zope.app.publication.zopepublication import ZopePublication
from zope.component import queryView, queryDefaultViewName
from zope.proxy import removeAllProxies
from zope.publisher.interfaces.xmlrpc import IXMLRPCPresentation
from zope.security.checker import ProxyFactory

class XMLRPCPublication(ZopePublication):
    """XML-RPC publication handling."""

    def traverseName(self, request, ob, name):
        """Traverse the name.

        The method should try the following things in this order:

        1. Check whether ob is a view; if so try to find a public method
           having the passed name.

        2. If the ob is not a view, then we try to find a view for it. This
           can be done in two ways:

           (a) Look whether there is a view registered for this name.

           (b) Check whether the default view has a matching method called name.

        3. See whether the object has a subobject of this name. This test is
           done last, since this is done by ZopePublication, and it knows how
           to create all the correct error messages. No need for us to do that.

        """
        naked_ob = removeAllProxies(ob)

        # Use the real view name
        view_name = name
        if view_name.startswith('@@'):
            view_name = view_name[2:]

        # If ob is a presentation object, then we just get the method
        if IXMLRPCPresentation.isImplementedBy(naked_ob) and \
               hasattr(ob, view_name):
            return ProxyFactory(
                ContextWrapper(getattr(ob, view_name), ob, name=view_name))

        # Let's check whether name could be a view 
        view = queryView(ob, view_name, request)
        if view is not None:
            return ProxyFactory(ContextWrapper(view, ob, name=view_name))

        # Now let's see whether we have a default view with a matching method
        # name
        defaultName = queryDefaultViewName(ob, request)

        if defaultName is not None:
            view = queryView(ob, defaultName, request, object)
            if hasattr(view, view_name):
                return ProxyFactory(ContextWrapper(getattr(view, view_name), ob,
                                                   name=view_name))

        # See whether we have a subobject
        return super(XMLRPCPublication, self).traverseName(request, ob, name)


# For now, have a factory that returns a singleton
class XMLRPCPublicationFactory:

    def __init__(self, db):
        self.__pub = XMLRPCPublication(db)

    def __call__(self):
        return self.__pub
