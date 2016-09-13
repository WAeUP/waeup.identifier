Installation
============

`waeup.identifier` is based on `kivy`_. Installing `kivy`_, requires
several libs to be installed. For convenience we created suitable
`ansible`_ playbooks that can (at least on Debian_-based systems)
install all required stuff at once - including raspbian and ubuntu.

On a Raspberry


Local dev environment
---------------------

To install kivy in a local virtualenv on the local host, run the
respective ansible playbook like this::

  $ ansible-playbook -i "localhost," -c local -K ansible/install-kivy-playbook.yml

This will ask for a SUDO password (``-K``) and install kivy in a local
virtualenv in ``/home/<USERNAME>/venv34/``.

If you want to install in a custom dir on localhost, do::

  $ ansible-playbook -i "localhost," -c local -e "venv_path=`pwd`/venv34" -K ansible/install-kivy-playbook.yml

I.e., set the `venv_path` variable to a path where you want to install
everything.

Please note, that we use Python 3.4 for kivy_ install.

.. _ansible: https://www.ansible.com/
.. _Debian: https://debian.org/
.. _kivy: https://kivy.org/
