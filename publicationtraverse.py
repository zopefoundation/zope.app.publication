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

$Id: publicationtraverse.py,v 1.12 2004/03/05 22:09:13 jim Exp $
"""

from zope.component import queryView
from zope.publisher.interfaces import NotFound
from types import StringTypes
from zope.security.checker import ProxyFactory

from zope.proxy import removeAllProxies
from zope.app.traversing.namespace import namespaceLookup
from zope.app.traversing.namespace import parameterizedNameParse
from zope.publisher.interfaces import IPublishTraverse

class DuplicateNamespaces(Exception):
    """More than one namespace was specified in a request"""

class UnknownNamespace(Exception):
    """A parameter specified an unknown namespace"""

class PublicationTraverse:

    def traverseName(self, request, ob, name):
        nm = name # the name to look up the object with

        if name and name[:1] in '@+':
            # Process URI segment parameters.
            ns, nm, parms = parameterizedNameParse(name)

            unknown_parms = ()
            for pname, pval in parms:
                pset = getattr(self, "_parameterSet%s" % pname, self) # marker
                if pset is self:
                    # We don't know about this one
                    unknown_parms += ((pname, pval),)
                else:
                    pset(pname, pval, request)

            if ns:
                ob2 = namespaceLookup(name, ns, nm, unknown_parms, ob, request)
                return ProxyFactory(ob2)

            if unknown_parms:
                nm = "%s;%s" % (
                    nm,
                    ';'.join(["%s=%s" % (parm[0], parm[1])
                              for parm in unknown_parms])
                    )

            if not nm:
                # Just set params, so skip
                return ob

        if nm == '.':
            return ob

        if IPublishTraverse.providedBy(removeAllProxies(ob)):
            ob2 = ob.publishTraverse(request, nm)
        else:
            adapter = queryView(ob, '_traverse', request, self) # marker
            if adapter is not self:
                ob2 = adapter.publishTraverse(request, nm)
                # ob2 will be security proxied here becuase the adapter
                # was security proxied.
            else:
                raise NotFound(ob, name, request)

        return ProxyFactory(ob2)

class PublicationTraverser(PublicationTraverse):

    def traversePath(self, request, ob, path):

        if isinstance(path, StringTypes):
            path = path.split('/')
            if len(path) > 1 and not path[-1]:
                # Remove trailing slash
                path.pop()
        else:
            path = list(path)

        # Remove single dots
        path = [x for x in path if x != '.']

        path.reverse()

        # Remove double dots
        while '..' in path:
            l = path.index('..')
            if l < 0 or l+2 > len(path):
                break
            del path[l:l+2]

        pop = path.pop

        while path:
            name = pop()
            ob = self.traverseName(request, ob, name)

        return ob
