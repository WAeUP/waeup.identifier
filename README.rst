waeup.identifier
================

Identify WAeUP students biometrically.

Provides a package that helps with fingerprint scanning/verifying,
which are stored in WAeUP student portals.


User Install
------------

For people that only want to simply use the software::

  $ pip install waeup.identifier

Afterwards the commandline tool (`waeup_identifier`) should be
available.


Developer Install
-----------------

It is recommended to setup sources in a virtual environment::

  $ virtualenv py32         # only Python 3.2 is supported currently
  $ source py32/bin/activate
  (py32) $

Get the sources::

  (py32) $ git clone https://github.com/ulif/waeup.identifier.git
  (py32) $ cd waeup.identifier

Install packages for testing::

  (py32) $ python setup.py dev

Running tests::

  (py32) $ py.test

We also support `tox` to run tests for all supported Python versions::

  (py32) $ pip install tox
  (py32) $ tox

Of course you must have the respective Python versions installed
(currently 3.2 only).

Running the test coverage detector::

  (py32) $ py.test --cov=waeup.identifier   # for cmdline results
  (py32) $ py.test --cov=waeup.identifier --cov-report=html

The latter will generate HTML coverage reports in a subdirectory.


Docs Install
------------

To install/generate the documentation locally, you first have to
install the needed tools::

  (py32) $ python setup.py docs
  (py32) $ cd doc
  (py32) $ make html

Will generate the documentation in a subdirectory.
