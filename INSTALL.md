MiniNDN-WiFi Installing Instructions
================================

### What equipment will I need?

Basically, you'll need a laptop/desktop with a recent Linux distro (Ubuntu, Fedora).
We recommend Ubuntu. For this guide, the _Ubuntu 16.04 64bit LTS_ was used.
Also, note that you'll need administrative privileges in order to download and install
extra packages and also to execute **Mini-NDN Wifi**.

### Installing **Mini-NDN Wifi**

If you have all the dependencies (see sections below) installed simply clone this repository and run:

    sudo ./install.sh -iw

else if you don't have the dependencies, the following command will install them along with Mini-NDN:

    sudo ./install.sh -a

else if you want to install the dependencies manually, follow the instructions below:

### Installing NDN

Each node in **Mini-NDN Wifi** will run the official implementation of NDN. The following dependencies are needed:

Mini-NDN Wifi uses NFD and ndn-tools.

To install NFD:
http://named-data.net/doc/NFD/current/INSTALL.html

To install ndn-tools:
https://github.com/named-data/ndn-tools

### Installing Mininet-Wifi

**Mini-NDN Wifi** depends on Mininet-Wifi. To install it:

    git clone --depth 1 https://github.com/intrig-unicamp/mininet-wifi.git
    
After you've cloned the repository, you need to `cd` to that directory and issue these commands:

    git checkout ndn
    sudo util/install.sh -Wlnfv
    
Check if everything is working:

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
