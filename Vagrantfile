# -*- mode: ruby -*-
# vi: set ft=ruby :

$script = <<SCRIPT

git clone --depth 1 https://github.com/named-data/mini-ndn.git
cd mini-ndn
./install.sh -a
SCRIPT

Vagrant.configure(2) do |config|
  config.vm.box = "bento/ubuntu-16.04"
  config.vm.provision "shell", privileged: false, inline: $script
  config.vm.provider "virtualbox" do |vb|
    vb.name = "mini-ndn_box"
    vb.memory = 2000
    vb.cpus = 2
  end
end
