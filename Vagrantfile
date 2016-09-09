# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  # Debian base boxes: see https://wiki.debian.org/Teams/Cloud/VagrantBaseBoxes
  config.vm.box = "debian/jessie64"
  config.vm.define "kivy" do |machine|
    # Create a private network, which allows host-only access to the machine
    # using a specific IP.
    machine.vm.hostname = "kivy.sample.org"
    machine.vm.network "private_network", ip: "192.168.34.33"
    # machine.vm.synced_folder "../data", "/vagrant_data"
    machine.vm.provider "virtualbox" do |vb|
      vb.gui = false
      vb.memory = "2048"
      vb.name = "kivy"
    end
    # ansible does not need a client, but needs python-apt to install packages
    config.vm.provision "shell", inline: "apt-get install --yes python-apt"
    machine.vm.provision "ansible" do |ansible|
      ansible.verbose = "v"
      ansible.playbook = "ansible/install-kivy-playbook.yml"
    end
  end
end
