# Mini-NDN in [VirtualBox](https://www.virtualbox.org/) using [vagrant](https://www.vagrantup.com/).

### [RECOMMENDED] Mini-NDN Vagrant Box

We have a Mini-NDN pre-installed in a vagrant box. The box can be found [here](https://app.vagrantup.com/sdulal/boxes/mini-ndn). For suggested Mini-NDN resource allocation,
Here's an example [`Vagrantfile`](https://gerrit.named-data.net/c/mini-ndn/+/6426/18/vagrant/Vagrantfile):
```ruby
# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.configure("2") do |config|
  config.vm.box = "sdulal/mini-ndn"
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "4096"
    vb.cpus = "4"
    vb.name = "mini-ndn-box"
  end
end
```
----

### [NOT RECOMMENDED] Building from scratch with `vagrant` and VirtualBox containing Mini-NDN

* Download and install VirtualBox and Vagrant
  * https://www.vagrantup.com/downloads
  * https://www.virtualbox.org/wiki/Downloads
* To create and start fresh virtual machine:
  * Create a file called "Vagrantfile" with this basic setup:
    ```ruby
    # -*- mode: ruby -*-
    # vi: set ft=ruby :
    Vagrant.configure("2") do |config|
      config.vm.box = "bento/ubuntu-20.04"
      config.disksize.size = '40GB'
      config.vm.provider "virtualbox" do |vb|
        vb.memory = 4096
        vb.cpus = 4
        vb.name = "mini-ndn-box"
      end
    end
    ```
  * Open your terminal or command line in the directory that has Vagrantfile
  * Start the virtual machine with,
    `$ vagrant up`
  * (If required) The username/password for the vm are both `vagrant`.

* To install Mini-NDN, use the following commands:
    ```bash
    git clone https://github.com/named-data/mini-ndn.git
    cd mini-ndn
    ./install.sh --source
    ```
* To test mini-ndn:
    * while still in the `mini-ndn` directory, enter
      ```bash
      sudo python examples/mnndn.py
      ```
    * If it worked, You will see the Mini-NDN CLI. Enter `exit` to close the CLI.

(Additional optional "not really needed" steps)
* To clean and export vm as Vagrant Box:
    * while in vm, enter these to clean:
      ```bash
      cd
      sudo apt-get clean
      sudo dd if=/dev/zero of=/EMPTY bs=1M
      sudo rm -f /EMPTY
      cat /dev/null > ~/.bash_history && history -c && exit
      ```
    * Close the vm window and open a terminal in the same directory as the `Vagrantfile`.
    * In the terminal, type this command where `vb_name` is the name of the vm defined in `Vagrantfile`, and `box_name` any name for the output `.box` file
      ```bash
      vagrant package --base vb_name --output box_name.box
      ```