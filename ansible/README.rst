Installing and Provisioning with ansible
========================================

We provide some `ansible`_ playbooks to ease installation and
provisioning on RaspberryPI_ (raspbian) or other Debian-based distros.

All `ansible`_-related stuff can be found in the projects ``ansible/``
subdir.


Get ansible_
------------

On Ubuntu/Debian::

  $ sudo apt-get install ansible

Please make sure, your `ansible` is not too old. Version 2.x+ would be
nice::

  $ ansible --version
  ansible 2.1.1.0

If it is too old, Ubuntu users can get a more recent version from the
`ansible/ansible` PPA. It can be activated with `add-apt-repository`
command. [1]_

::

  $ sudo apt-get install software-properties-common  #  Ubuntu 14.04+
  $ sudo add-apt-repository ppa:ansible/ansible
  $ sudo apt-get update
  $ sudo apt-get install ansible


The `hosts` file is an ansible_ inventory file. The IP set in it must
match the real IP of your local raspberry pi.

It also sets a username to connect to the device. If you use another
username, replace `pi`.

Check Basic Ansible Connectivity
--------------------------------

First, make sure you can SSH into your RaspberryPI as user ``pi``::

  $ ssh -l pi 192.168.45.244

(but with the real IP of your RaspberryPI).

Do not skip this step as it prepares SSH to flawlessly connect to your device
(storing the host id, etc.).

Then see, if `ansible` can connect to your RaspberryPI::

  $ ansible -i 192.168.32.86, all -k -u pi -m setup

Please note the trailing comma after the IP number.

Again, use the real IP of your RaspberryPI instead of
``192.168.32.86`` (don't forget the trailung comma). You will be asked
for the SSH password.

If you have an `hosts` file with appropriate settings (IP and
username) and configured passwordless login on your Raspberry PI, you
can instead do::

  $ ansible -i hosts all -m setup

These should list plenty of infos about your raspberry in green
color. Red means: something went wrong.


Initial Provisioning
--------------------

Preparation:

Your RaspberryPI should be

- up and running
- have an internet connection

You should have run the steps above at least once from every host you
connect from.

Then you can run the local ansible setup playbook like this::

  $ ansible-playbook -i 192.168.122.12, -u pi -k setup_raspi_playbook.yml

Please note the trailing comma after the IP number.

The username ``pi`` and the IP number must, of course be set to match
your local settings.

The playbook will ask for the SSH password of the user set with ``-u``
(default: ``raspberry``).

This playbook will also clone the `waeup.identifier` repository.


.. _ansible: https://www.ansible.com/
.. _RaspberryPI: https://raspberrypi.org

.. [1] On Ubuntu 12.04 you have to install `python-software-properties`
       instead of `software-properties-common`
