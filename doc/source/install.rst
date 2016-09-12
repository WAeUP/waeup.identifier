Installation
============

Local dev environment
---------------------

To install kivy in a local virtualenv on the local host, run the
respective ansible playbook like this::

  $ ansible-playbook -i "localhost," -c local -K ansible/install-kivy-playbook.yml

This will ask for a SUDO password (``-K``) and install kivy in a local
virtualenv in ``/home/<USERNAME>/venv27/``.

If you want to install in a custom dir on localhost, do::

  $ ansible-playbook -i "localhost," -c local -e "venv_path=`pwd`/venv27" -K ansible/install-kivy-playbook.yml

I.e., set the `venv_path` variable to a path where you want to install
everything.
