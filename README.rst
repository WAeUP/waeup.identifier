waeup.identifier
================

Identify WAeUP students biometrically.


.. image:: https://travis-ci.org/WAeUP/waeup.identifier.svg?branch=master
   :target: https://travis-ci.org/WAeUP/waeup.identifier

Scan/verify fingerprints of Kofa_ students. `waeup.identifier` uploads
taken fingerprints and can verify student fingerprints after that. Kofa_
is an open source student management portal from WAeUP_ .

Full documentation is available at

  https://waeupidentifier.readthedocs.io

Requirements
------------

`waeup.identifier` runs on Python 3.4.

You need Kivy_ and fpscan_ installed.

There are many ways to install `kivy` on your system. Please see the
Kivy_ homepage for a detailed discussion.

`waeup.identifier` is designed to be run on a RaspberryPI_ 3, but also
runs on ordinary laptops and desktop computers.

While a fingerprint scanner device is not strictly neccessary to run
`waeup.identifier`, it also makes not much sense to run it without.

.. note:: To ease install on RaspberryPI_ we provide a bunch of playbooks for
          use with `ansible`_. The ansible playbooks can also be used for
          provisioning other machines. See the ``ansible/`` subdir of
          `waeup.identifier` for details.


User Install
------------

For people that only want to simply use the software::

  $ sudo pip install waeup.identifier

Afterwards the commandline tool (`waeup_identifier`) should be
available.


Developer Install
-----------------

It is recommended to setup sources in a virtual environment::

  $ virtualenv py34 -p python3.4    # only Python 3.4 is supported currently
  $ source py34/bin/activate
  (py34) $

Then, install `Cython` and Kivy_ (in that order)::

  (py34) $ pip install Cython
  (py34) $ pip install kivy

Please note that especially Kivy_ requires a lot of special libraries to run.

Get the sources::

  (py34) $ git clone https://github.com/WAeUP/waeup.identifier.git
  (py34) $ cd waeup.identifier

Install packages for testing/developing::

  (py34) $ python setup.py dev

This will also install the ``waeup_identifier`` script in your virtual
environment ``bin/`` dir (and a `fake_kofa_server` script, useful for
testing).

Running tests::

  (py34) $ py.test

We also support `tox` to run tests for all supported Python versions::

  (py34) $ pip install tox
  (py34) $ tox

Of course you must have the respective Python versions installed
(currently 3.4 only).

Running the test coverage detector::

  (py34) $ KIVY_NO_ARGS=1 py.test --cov=waeup.identifier   # for cmdline results
  (py34) $ KIVY_NO_ARGS=1 py.test --cov=waeup.identifier --cov-report=html

The latter will generate HTML coverage reports in a subdirectory.

The env var setting (`KIVY_NO_ARGS`) at the beginning keeps `kivy` from parsing
command line arguments.


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
  Starting server at 127.0.0.1:61616
  No entries created. Restart with `-- -p' to create.
  Press ^C (Ctrl-c) to abort.

and will listen for XMLRPC requests on localhost port 61616. It
requires basic authentication with ``mgr`` as username and ``mgrpw``
as password.

You can also start the server with a prepopulated db (which will
vanish when the server stops) like this::

  (py34) $ fake_kofa_server -- -p
  Starting server at 127.0.0.1:61616
  Created fake entry: AA11111
  Created fake entry: BB11111
  Press ^C (Ctrl-c) to abort.

Programmatically, the fake kofa server can be started like this:

  >>> import threading
  >>> from waeup.identifier.testing import AuthenticatingXMLRPCServer
  >>> server = AuthenticatingXMLRPCServer('127.0.0.1', 16161)
  >>> server_thread = threading.Thread(
  ...     target=server.serve_forever
  ...     )
  >>> server_thread.daemon = True
  >>> server_thread.start()

When the server runs, you can try to connect to it via `xmlrpclib`
(Python 2.x) or `xmlrpc.client` (Python 3.x). Please note, that the
`fake_kofa_server` by default listens on localhost port 616161.

  >>> from xmlrpc.client import ServerProxy  # Python 3.x only
  >>> s = ServerProxy("http://mgr:mgrpw@localhost:16161")
  >>> s.ping(42)
  ['pong', 42]

See WAeUP Kofa docs or local webservice tests for method details.

  >>> server.shutdown()


.. _ansible: https://www.ansible.com/
.. _fpscan: https://github.com/ulif/fpscan
.. _Kivy: http://kivy.org/
.. _Kofa: https://pypi.python.org/pypi/waeup.kofa
.. _RaspberryPI: https://raspberrypi.org
.. _WAeUP: https://waeup.org/
