# Mini-NDN in [VirtualBox](https://www.virtualbox.org/) using [vagrant](https://www.vagrantup.com/)

### [RECOMMENDED] Mini-NDN Vagrant Box

We provide a Vagrant box with Mini-NDN pre-installed. The box can be found
[here](https://portal.cloud.hashicorp.com/vagrant/discover/netlab-memphis-minindn).
For suggested Mini-NDN resource allocation, here's an example [`Vagrantfile`](Vagrantfile) using VirtualBox:
```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "netlab-memphis-minindn/minindn-0.7.0"
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "4096"
    vb.cpus = "4"
    vb.name = "mini-ndn-box"
  end
end
```
----

For those on ARM64 MacOS devices, you can instead use our provided VMWare image.
You will need the [Vagrant VMWare Utility](https://developer.hashicorp.com/vagrant/docs/providers/vmware/installation)
installed. You can then initialize the Vagrant box using `vagrant up --provider vmware_desktop`

This provider is not as well supported and may encounter minor issues.

```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "netlab-memphis-minindn/minindn-0.7.0"
  config.vm.provider "vmware_desktop" do |vb|
    vb.memory = "4096"
    vb.cpus = "4"
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
    Vagrant.configure("2") do |config|
      config.vm.box = "bento/ubuntu-22.04"
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
    ./install.sh
    ```
* To test mini-ndn:
    * while still in the `mini-ndn` directory, enter
      ```bash
      sudo python examples/mnndn.py
      ```
    * If it worked, You will see the Mini-NDN CLI. Enter `exit` to close the CLI.

(Recommended steps for distribution)
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
