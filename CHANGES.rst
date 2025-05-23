=======
CHANGES
=======

5.1 (unreleased)
----------------

- Add support for Python 3.12, 3.13.

- Drop support for Python 3.7, 3.8.


5.0 (2023-02-08)
----------------

- Add support for Python 3.10, 3.11.

- Drop support for Python 2.7, 3.5, 3.6.


4.5 (2020-11-05)
----------------

- Add support for Python 3.8 and 3.9.

- Update the tests to ``zope.app.wsgi >= 4.3``.


4.4 (2020-05-14)
----------------

- Drop support for ``python setup.py test``.


4.3.2 (2019-12-04)
------------------

- Fix deprecation warning in tests.


4.3.1 (2019-07-01)
------------------

- Updated expected doc output to match latest library versions (yes, again).

- Fixed supported Python versions in .travis.yml.

- Avoid passing unicode text to logging.Logger.warning() on Python 2 (`issue 8
  <https://github.com/zopefoundation/zope.app.publication/issues/8>`_).


4.3.0 (2018-10-09)
------------------

- Drop Python 3.4 support and added 3.7.

- Updated expected doc output to match latest library versions.

- Removed all deprecation warnings.


4.2.1 (2017-04-17)
------------------

- Include ``MANIFEST.in`` since it is needed for pip install.


4.2.0 (2016-11-23)
------------------

- Update the code to be compatible with ``transaction >= 2.0``.

- Update tests to be compatible with ``ZODB >= 5.1``, thus requiring at least
  this version for the tests.

- Drop Python 3.3 support.


4.1.0 (2016-08-08)
------------------

- Test against released final versions, thus requiring ``zope.app.http`` >= 4.0
  (test dependency).


4.0.0 (2016-08-08)
------------------

- Claim compatibility to Python 3.4 and 3.5 and drop support for Python 2.6.

- Improve the publication factory lookup by falling back to a more generic
  registration if the specific factory chooses not to handle the request after
  all.

- Relax ZODB dependency to allow 3.10dev builds from SVN.

- Introduce ZopePublication.callErrorView as a possible hook point.


3.14.0 (2012-03-09)
-------------------

- Replace ZODB.POSException.ConflictError with
  transaction.interfaces.TransientError. The latter should be a more generic
  signal to retry a transaction/request.
  This requires ZODB3 >= 3.10.0 and transaction >= 1.1.0.

- Get rid of ZODB dependency.


3.13.2 (2011-08-04)
-------------------

- Add missing test dependency on zope.testing.

- Remove test dependency on zope.app.exception.


3.13.1 (2011-03-14)
-------------------

- Test fix: HTTP request should not have leading whitespace.


3.13.0 (2011-01-25)
-------------------

- Reenabled a test which makes sure ``405 MethodNotAllowed`` is returned
  when PUT is not supported. This requires at least version 3.10 of
  zope.app.http.


3.12.0 (2010-09-14)
-------------------

- Use the standard libraries doctest module.

- Include the ``notfound.txt`` test again but reduce its scope to functionality
  relevant to this distribution.

- Notify with IStartRequestEvent at the start of the request publication
  cycle.

3.11.1 (2010-04-19)
-------------------

- Fix up tests to work with newer zope.app.wsgi release (3.9.0).

3.11.0 (2010-04-13)
-------------------

- Don't depend on zope.app.testing and zope.app.zcmlfiles anymore in
  the tests.

3.10.2 (2010-01-08)
-------------------

- Lift the test dependency on zope.app.zptpage.


3.10.1 (2010-01-08)
-------------------

- make zope.testing an optional (test) dependency

- Fix tests using a newer zope.publisher that requires zope.login.

3.10.0 (2009-12-15)
-------------------

- Moved EndRequestEvent and IEndRequestEvent to zope.publisher.

- Moved BeforeTraverseEvent and IBeforeTraverseEvent to zope.traversing.

- Removed dependency on zope.i18n.

- Import hooks functionality from zope.component after it was moved there from
  zope.site.

- Import ISite from zope.component after it was moved there from
  zope.location.

3.9.0 (2009-09-29)
------------------

- An abort within handleExceptions could have failed without logging what
  caused the error. It now logs the original problem.

- Moved registration of and tests for two publication-specific event handlers
  here from zope.site in order to invert the package dependency.

- Declared the missing dependency on zope.location.

3.8.1 (2009-06-21)
------------------

- Bug fix: The publication traverseName method used ProxyFactory
  rather than the publication proxy method.

3.8.0 (2009-06-20)
------------------

- Added a proxy method that can be overridden in subclasses to control
  how/if security proxies are created.

- Replaced zope.deprecation dependency with backward-compatible imports

3.7.0 (2009-05-23)
------------------

- Moved the publicationtraverse module to zope.traversing, removing the
  zope.app.publisher -> zope.app.publication dependency (which was a
  cycle).

- Moved IHTTPException to zope.publisher, removing the dependency
  on zope.app.http.

- Moved the DefaultViewName API from zope.app.publisher.browser to
  zope.publisher.defaultview, making it accessible to other packages
  that need it.

- Look up the application controller through a utility registration
  rather than a direct reference.

3.6.0 (2009-05-18)
------------------

- Use ``zope:adapter`` ZCML directive instead of ``zope:view``.
  This avoid dependency on ``zope.app.component``.

- Update imports from ``zope.app.security`` to ``zope.authentication`` and
  ``zope.principalregistry``.

- Use ``zope.browser.interfaces.ISystemError`` to avoid dependency on
  ``zope.app.exception``.

- Refactored tests so they can run successfully with ZODB 3.8 and 3.9.

3.5.3 (2009-03-13)
------------------

- Adapt to the removal of IXMLPresentation from zope.app.publisher which
  was removed to adapt to removal of deprecated interfaces from zope.component.

3.5.2 (2009-03-10)
------------------

- Use ISkinnable.providedBy(request) instead of IBrowserRequest as condition
  for calling setDefaultSkin. This at the same time removes dependency to
  the browser part of zope.publisher.

- Remove deprecated code.

- Use built-in set class instead of the deprecated sets.Set and thus
  don't cause deprecation warning in Python 2.6.

3.5.1 (2009-01-31)
------------------

- Import ISite from zope.location.interfaces instead of deprecated place
  in zope.app.component.interfaces.

3.5.0 (2008-10-09)
------------------

- Now ``zope.app.publication.zopepublication.ZopePublication`` annotates the
  request with the connection to the main ZODB when ``getApplication`` is
  called.

- Removed support for non-existent Zope versions.


3.4.3 (2007-11-01)
------------------

- Removed unused imports.

- Resolve ``ZopeSecurityPolicy`` deprecation warning.


3.4.2 (2007-09-26)
------------------

- Added missing files to egg distribution.


3.4.1 (2007-09-26)
------------------

- Added missing files to egg distribution.


3.4.0 (2007-09-25)
------------------

- Initial documented release.

- Reflect changes form ``zope.app.error`` refactoring.
