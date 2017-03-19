Installing and Provisioning with ansible
========================================

We provide some `ansible`_ playbooks to ease installation and
provisioning on RaspberryPI_ (raspbian) or other Debian-based distros.

The RaspberryPI is assumed to have the default 7" touch screen
attached.

All `ansible`_-related stuff can be found in the projects ``ansible/``
subdir. In the following we show how to provision a running
RaspberryPI_ connected to the same network as your local machine.


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


Check SSH Connectivity
----------------------

First, make sure you can SSH into your RaspberryPI_ as user ``pi`` [2]_ ::

  $ ssh -l pi 192.168.45.244

(but with the real IP of your RaspberryPI).

Then, unless done already, change the password of the `pi` user::

  $ passwd

Do not skip these steps as they prepare SSH to flawlessly connect to your device
(storing the host id, etc.).


Check Basic Ansible Connectivity
--------------------------------

Then see, if `ansible`_ can connect as user ``pi`` to your
RaspberryPI::

  $ ansible -i 192.168.32.86, all -k -u pi -m setup

Please note the trailing comma after the IP number.

Again, use the real IP of your RaspberryPI instead of
``192.168.32.86`` (don't forget the trailung comma). You will be asked
for the SSH password and replace ``pi`` with your real user if you do
not use the default.

If you have an `hosts` file with appropriate settings (IP and
username) and configured passwordless login on your Raspberry PI, you
can instead do::

  $ ansible -i hosts all -m setup

These should list plenty of infos about your raspberry in green
color. Red means: something went wrong.

The `hosts` file is an ansible_ inventory file. The IP set in it must
match the real IP of your local Raspberry PI.

It also sets a username to connect to the device. If you use another
one, replace `pi` with the username you really use.


Initial Provisioning of a RaspberryPI
-------------------------------------

Preparation:

Your RaspberryPI should be

- up and running
- have an internet connection
- have a changed password or accept one of your local SSH keys

You should have run the steps above at least once.

Then carefully adjust the variables set in the `setup_raspi_playbook.yml`
header using your editor. Currently there are four of them:

  - `repo_path`: leave it untouched
  - `device_id`: if you are about to provision multiple devices, you can give
       each one a different name. This makes it easier to distinguish their
       configs later on. The name should be one string without whitespaces and
       made of ASCII chars only.
  - `reverse_ssh_host`: ip number or hostname of a machine for reverse SSH.
       This is the machine to which we want to connect to and create a tunnel
       at to our device. Ignore, if you do not understand what this is for.
  - `reverse_ssh_port`: the port on the remote host, we will use for reverse
       ssh. We will use this port to connect back to the device, once the
       reverse tunnel was started. Again, ignore, if you don't know what all
       that means.
  - `new_password`: the password to set for the connecting ssh user. The
       default password we set is ``fading-remedy-pony``. It is not safe to
       leave this password unchanged.
  - `set_password`: set to ``false`` if you don't want to set the password.

Then you can run the local ansible setup playbook like this::

  $ ansible-playbook -i 192.168.122.12, -u pi -k setup_raspi_playbook.yml

Please note the trailing comma after the IP number.

The username ``pi`` and the IP number must, of coursei, be set to match
your local settings.

The playbook will ask for the SSH password of the user set with ``-u``
(default: ``raspberry``).

This playbook will also clone the `waeup.identifier` repository.

.. note:: The raspberry-pi setup will take *huge* amounts of time for updating,
          depending on your internet connection and SD-card quality/speed.

          If you ssh into your raspi device once and run::

            $ sudo apt-get update
            $ sudo aptitude safe-upgrade

          you will be able to track changes and can check whether everything is
          still working. A later `ansible` run will be much shorter then.


Remote Maintenance (optional)
-----------------------------

If you want to prepare your freshly provisioned RaspberryPI for remote
maintenance, it is sufficient to run the `setup_raspi_playbook.yml` playbook.
It prepares your device to create a reverse ssh tunnel to a remote server and
also runs the `setup_ssh_playbook.yml` automatically to harden the SSH server
config on your device.

The raspi setup will also create a local EC25519 SSH key for logging into the
maintenance machine (and starting a reverse ssh tunnel).

.. note:: The public key will be copied to the local `keys` directory
          (``.../.ssh/id_ed25519.pub``) and must be copied to the maintenance
          servers ``authorized_keys`` file manually.

The remote box has to be prepared as well for the new
client. Therefore, on the remote box, we normally allow only creation
of an SSH reverse tunnel back to the RaspberryPI device. This
poor-mans' teamviewer allows us to log into the RaspberryPI from some
central machine if only the device has an internet connection.

The remote machine (not the RaspberryPI) can be provisioned for this
purpose with the `setup_maintbox_playbook.yml`::

  $ ansible-playbook -i <REMOTE-BOX-IP>, -u <REMOTE-USER> -k -K setup_maintbox_playbook.yml

Here we have to provide an SSH password (``-k``) and a sudo password
(``-K``). Leave these options out, if you have other authentication
methods activated on your remote server.

The playbook will create a user `reverse` that is only allowed to
connect to create a reverse SSH tunnel back to itself.


Install `fpscan`_
-----------------

Preparation:

- Ansible must be installed locally
- The target system should be reachable via ansible (see above)

The `fpscan`_ commandline utility is a little C program for creating
fingerprint scans. `waeup.identifier` deploys it to do the actual
scans.

Because `fpscan`_ is available as source code only, the
``install_fpscan_playbook.yml`` creates a local build dir in the SSH
users home, then builds and installs `fpscan`_.


Install `kivy`_
---------------

Preparation:

- Ansible must be installed locally
- The target system should be reachable via ansible (see above)

This playbook installs `kivy`_ in a virtualenv on the target machine.

The virtualenv will be created by `ansible`_ and is by default located
in the remote user's home dir. It can be set via the playbook var
``venv_path``.


Local dev environment
---------------------

To install `kivy`_ in a local virtualenv on the local host, run the
respective ansible playbook like this::

  $ ansible-playbook -i "localhost," -c local -K ansible/install_kivy_playbook.yml

This will ask for a SUDO password (``-K``) and install kivy in a local
virtualenv in ``/home/<USERNAME>/venv34/``.

If you want to install in a custom dir on localhost, do::

  $ ansible-playbook -i "localhost," -c local -e "venv_path=`pwd`/venv34" -K ansible/install_kivy_playbook.yml

I.e., set the `venv_path` variable to a path where you want to install
everything.

Please note, that we use Python 3.4 for kivy_ install.


.. _ansible: https://www.ansible.com/
.. _Debian: https://debian.org/
.. _fpscan: https://github.com/ulif/fpscan/
.. _kivy: https://kivy.org/
.. _RaspberryPI: https://raspberrypi.org

.. [1] On Ubuntu 12.04 you have to install `python-software-properties`
       instead of `software-properties-common`
.. [2] ``pi`` is the default user in Raspbian. If you created a
       different user to connect to your Raspberry PI, you should of
       course use that.
