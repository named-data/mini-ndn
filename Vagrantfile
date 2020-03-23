# -*- mode: ruby -*-
# vi: set ft=ruby :

$script = <<SCRIPT
ln -s /vagrant /home/vagrant/mini-ndn

# Check if install.sh is present or someone just copied the Vagrantfile directly
if [[ -f /home/vagrant/mini-ndn/install.sh ]]; then
  pushd /home/vagrant/mini-ndn
else
  # Remove the symlink
  rm /home/vagrant/mini-ndn
  git clone --depth 1 https://github.com/named-data/mini-ndn.git
  pushd mini-ndn
fi
./install.sh -qa

SCRIPT

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/bionic64"
  config.vm.provision "shell", privileged: false, inline: $script
  config.vm.provider "virtualbox" do |vb|
    vb.name = "mini-ndn_box"
    vb.memory = 4096
    vb.cpus = 4
  end
end
