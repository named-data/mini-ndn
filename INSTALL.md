Mini-NDN Installation Instructions
================================

### What equipment will I need?

For this guide, you will need a laptop/desktop with a recent version
of a Linux distro such as Ubuntu or any of its variants. Fedora is not
officially supported but has also been reported to work for some
users. For this guide, the _Ubuntu 18.04 LTS_ release was used.
Also, note that you'll need administrative privileges in order to
download and install extra packages and also to execute **Mini-NDN**.

### Installing **Mini-NDN**

NOTE: Mini-NDN, while providing a high level of emulation of hosts,
requires programs to be installed onto your computer. It will not work
if they are not installed. If you do not want NDN software installed
onto your computer, you can use a virtual machine, which can be quite
simply set up with the provided vagrantfile.

If you have all the dependencies (see sections below) installed simply clone this repository and run:

    ./install.sh -i

else if you don't have the dependencies, the following command will install them from source along with Mini-NDN:

    ./install.sh -a

If you want to install the dependencies manually or from the Named Data PPA, follow the instructions below:

### Installing NDN

Each node in **Mini-NDN** will run the official implementation of NDN installed on your system. The following dependencies are needed:

Mini-NDN uses NFD, NLSR, and ndn-tools.

To install NFD:
https://named-data.net/doc/NFD/current/INSTALL.html

To install NLSR:
https://named-data.net/doc/NLSR/current/INSTALL.html

To install ndn-tools:
https://github.com/named-data/ndn-tools

Note that all three of these can be installed from the Named Data PPA. Instructions for setting it up can
be found in the NFD insallation instructions. Note that PPA and installs from source **cannot** be mixed.

###Special Instructions for PPA Installs

If you are using a custom nfd.conf file in an experiment, you should place it in /usr/local/etc/ndn/
rather than /etc/ndn/. This is to avoid a bug from the default configuration file for the PPA, which
is incompatiable with Mini-NDN.

### Installing Mininet

**Mini-NDN** is based on Mininet. To install Mininet:

First, clone Mininet from github:

    git clone --depth 1 https://github.com/mininet/mininet.git

After Mininet source is on your system, run the following command to
install Mininet core dependencies and Open vSwitch:

    ./util/install.sh -nv

To check if Mininet is working correctly, run this test:

    sudo mn --test pingall

This will print out a series of statements that show the test setup
and the results of the test. Look for `Results:` two-thirds of the way
down where it will indicate the percentage of dropped packets.
Your results should show "0% dropped (2/2 received)".

### Installing Infoedit

Infoedit is used to edit configuration files such as NFD configuration
file.

To install infoedit:
https://github.com/NDN-Routing/infoedit

### Verification

You can use these steps to verify your installation:

1. Issue the command: `sudo minindn --experiment=pingall --nPings=50`
2. When the `mini-ndn>` CLI prompt appears, the experiment has finished. On the Mini-NDN CLI, issue the command `exit` to exit the experiment.
3. Issue the command: `grep -c content /tmp/minindn/*/ping-data/*.txt`. Each file should report a count of 50.
4. Issue the command: `grep -c timeout /tmp/minindn/*/ping-data/*.txt`. Each file should report a count of 0.