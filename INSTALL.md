Mini-NDN Installing Instructions
================================

### What equipment will I need ?

Basically, you'll need a laptop/desktop with a recent Linux distro (Ubuntu, Fedora).
We recommend Ubuntu. For this guide, the _Ubuntu 14.04 LTS_ was used.
Also, note that you'll need administrative privileges in order to download and install
extra packages and also to execute **Mini-NDN**.

### Installing NDN

Each node in **Mini-NDN** will run the official implementation of NDN. The following dependencies are needed:

Mini-NDN uses NFD, NLSR, and ndn-tlv-ping.

To install NFD:
http://named-data.net/doc/NFD/current/INSTALL.html

To install NLSR:
http://named-data.net/doc/NLSR/current/INSTALL.html

To install ndn-tools:
https://github.com/named-data/ndn-tools

### Installing Mininet

**Mini-NDN** is based on Mininet. To install Mininet:
https://github.com/mininet/mininet/INSTALL

### Installing **Mini-NDN**

If you have all the dependencies installed simply clone this repository and run:

    sudo ./install.sh -i

else if you don't have the dependencies:

    sudo ./install.sh -mrfti

### Verification

Once everything is installed, the following command can be issued for verification

    sudo minindn --pingall 50 --ctime 180 ndn_utils/hyperbolic_conf_file/minindn.caida.conf

All the ping logs will be stored under /tmp/node-name/ping-data and the command will provide a
command line interface at the end.

When the "mininet>" CLI prompt appears, press CTRL+D to terminate the experiment.
Then, execute `ls /tmp/*/ping-data/*.txt | wc -l`, and expect to see "90".
Execute `cat /tmp/*/ping-data/*.txt | grep loss`, and expect to see "0% packet loss" on every line.
