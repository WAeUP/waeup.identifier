ansible
=======

This is the place for scripts helping with provisioning RaspberryPi
devices for use of `waeup.identifier`.

The `hosts` file is an ansible inventory file. The IP set in it must be set to the real IP of your local raspberry pi.

It also sets a username to connect to the device. If you use another
username, replace `pi`.


Initial Provisioning
--------------------

Preparation:

Your RaspberryPI should be

- up and running
- have an internet connection

For the following procedure you must be able to connect to your Raspi
device via SSH.

Then you can run the local ansible setup playbook like this::

  $ ansible-playbook -i 192.168.122.12, -u pi -k setup-raspi-playbook.yml

Please note the trailing comma after the IP number.

The username ``pi`` and the IP number must, of course be set to match
your local settings.

The playbook will ask for the SSH password of the user set with ``-u``
(default: ``raspberry``).
