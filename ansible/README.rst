ansible
=======

This is the place for scripts helping with provisioning RaspberryPi
devices for use of `waeup.identifier`. You must have `ansible`
installed on your local machine.

On Ubuntu/Debian::

  $ sudo apt-get install ansible

The `hosts` file is an ansible inventory file. The IP set in it must
be set to the real IP of your local raspberry pi.

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

If you have an `hosts` file with appropriate settings, you can instead
do::

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

  $ ansible-playbook -i 192.168.122.12, -u pi -k setup-raspi-playbook.yml

Please note the trailing comma after the IP number.

The username ``pi`` and the IP number must, of course be set to match
your local settings.

The playbook will ask for the SSH password of the user set with ``-u``
(default: ``raspberry``).
