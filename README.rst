waeup.identifier
================

Identify WAeUP students biometrically.


.. image:: https://travis-ci.org/WAeUP/waeup.identifier.svg?branch=master
   :target: https://travis-ci.org/WAeUP/waeup.identifier

Provides a package that helps with fingerprint scanning/verifying,
which are stored in WAeUP student portals.

.. warning:: We are going to give Kivy_ a try. As install is much more
             complicated with Kivy_, some or all of the following
             information might be wrong, misleading, or in other ways
             unhelpful.


Kivy Install
------------

Install we do in tests, based on Ubuntu 14.04.::

  $ sudo apt-add-repository ppa:kivy-team/kivy
  $ sudo apt-get update
  $ sudo apt-get install python3-kivy
  $ sudo apt-get install kivy-examples




User Install
------------

For people that only want to simply use the software::

  $ sudo pip install waeup.identifier

Afterwards the commandline tool (`waeup_identifier`) should be
available.

.. note:: The user install will be available after first
          release. Until then, please use developer install (see
          below).


Developer Install
-----------------

It is recommended to setup sources in a virtual environment::

  $ virtualenv py34 -p python3.4    # only Python 3.4 is supported currently
  $ source py34/bin/activate
  (py34) $

Get the sources::

  (py34) $ git clone https://github.com/ulif/waeup.identifier.git
  (py34) $ cd waeup.identifier

Install packages for testing/developing::

  (py34) $ python setup.py dev

This will also install the ``waeup_identifier`` script in your virtual
environment ``bin/`` dir (do *not* use the ``install`` command of
``setup.py`` for this; it will break your devel environment).

Running tests::

  (py34) $ py.test

We also support `tox` to run tests for all supported Python versions::

  (py34) $ pip install tox
  (py34) $ tox

Of course you must have the respective Python versions installed
(currently 3.4 only).

Running the test coverage detector::

  (py34) $ py.test --cov=waeup.identifier   # for cmdline results
  (py34) $ py.test --cov=waeup.identifier --cov-report=html

The latter will generate HTML coverage reports in a subdirectory.


Docs Install
------------

To install/generate the documentation locally, you first have to
install the needed tools::

  (py34) $ python setup.py docs
  (py34) $ cd doc
  (py34) $ make html

Will generate the documentation in a subdirectory.


Misc
----

There is a fake Kofa XMLRPC server included for use in tests. The
server tries to mimic WAeUP Kofa XMLRPC API while being much more
lightweight. It can be started using::

  (py34) $ fake_kofa_server

and will listen for XMLRPC requests on localhost port 61616. It
requires basic authentication with ``mgr`` as username and ``mgrpw``
as password.

Programmatically, the fake kofa server can be started like this:

  >>> import threading
  >>> from waeup.identifier.testing import AuthenticatingXMLRPCServer
  >>> server = AuthenticatingXMLRPCServer('127.0.0.1', 61616)
  >>> server_thread = threading.Thread(
  ...     target=server.serve_forever
  ...     )
  >>> server_thread.daemon = True
  >>> server_thread.start()

When the server runs, you can try to connect to it via `xmlrpclib`
(Python 2.x) or `xmlrpc.client` (Python 3.x). Please note, that the
`fake_kofa_server` by default listens on localhost port 14096.

  >>> from xmlrpc.client import ServerProxy  # Python 3.x only
  >>> s = ServerProxy("http://mgr:mgrpw@localhost:61616")
  >>> s.ping(42)
  ['pong', 42]

See WAeUP Kofa docs or local webservice tests for method details.

  >>> server.shutdown()


.. _Kivy: http://kivy.org/
