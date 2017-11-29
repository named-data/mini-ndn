Mini-NDN Installing Instructions
================================

### What equipment will I need?

Basically, you'll need a laptop/desktop with a recent Linux distro (Ubuntu, Fedora).
We recommend Ubuntu. For this guide, the _Ubuntu 14.04 LTS_ was used.
Also, note that you'll need administrative privileges in order to download and install
extra packages and also to execute **Mini-NDN**.

### Installing **Mini-NDN**

If you have all the dependencies (see sections below) installed simply clone this repository and run:

    sudo ./install.sh -i

else if you don't have the dependencies, the following command will install them along with Mini-NDN:

    sudo ./install.sh -emrfti

else if you want to install the dependencies manually, follow the instructions below:

### Installing NDN

Each node in **Mini-NDN** will run the official implementation of NDN. The following dependencies are needed:

Mini-NDN uses NFD, NLSR, and ndn-tools.

To install NFD:
http://named-data.net/doc/NFD/current/INSTALL.html

To install NLSR:
http://named-data.net/doc/NLSR/current/INSTALL.html

To install ndn-tools:
https://github.com/named-data/ndn-tools

### Installing Mininet

**Mini-NDN** is based on Mininet. To install Mininet:

First, clone Mininet from github:

    git clone --depth 1 https://github.com/mininet/mininet.git

After Mininet source is on your system, run the following command to install
Mininet core dependencies and Open vSwitch:

    ./util/install.sh -nv

To check if Mininet is working correctly, run this test:

    sudo mn --test pingall

This will print out a series of statements that show the test setup and the results of the test. Look
for `Results:` two-thirds of the way down where it will indicate the percentage of dropped packets.
Your results should show "0% dropped (2/2 received)".

### Installing Infoedit

Infoedit is used to edit configuration files such as NFD configuration file.

To install infoedit:
https://github.com/NDN-Routing/infoedit

### Verification

You can use these steps to verify your installation:

1. Issue the command: `sudo minindn --experiment=pingall --nPings=50`
2. When the `mini-ndn>` CLI prompt appears, the experiment has finished. On the Mini-NDN CLI, issue the command `exit` to exit the experiment.
3. Issue the command: `grep -c content /tmp/minindn/*/ping-data/*.txt`. Each file should report a count of 50.
4. Issue the command: `grep -c timeout /tmp/minindn/*/ping-data/*.txt`. Each file should report a count of 0.
