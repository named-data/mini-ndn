Mini-NDN Installing Instructions
================================

### What equipment will I need ?

Basically, you'll need a laptop/desktop with a recent Linux distro (Ubuntu, Fedora).
We recommend Ubuntu. For this guide, the _Ubuntu 14.04 LTS_ was used.
Also, note that you'll need administrative privileges in order to download and install
extra packages and also to execute **Mini-NDN**.

### Installing NDN

Each node in **Mini-NDN** will run the official implementation of NDN. Let's get it.

Mini-NDN uses NFD, NLSR, and ndn-tlv-ping.

To install NFD:
http://named-data.net/doc/NFD/current/INSTALL.html

To install NLSR:
http://named-data.net/doc/NLSR/current/INSTALL.html

To install ndn-tlv-ping:
https://github.com/named-data/ndn-tlv-ping

### Downloading and installing **Mini-NDN**

If you don't have it yet, you'll need to have _git_ installed first. In Ubuntu, that would be:

    sudo apt-get install git

Now, let's get the source code of **Mini-NDN**.
Go to your home directory and use the following command:

    git clone https://github.com/named-data/mini-ndn

As a result, there will be a directory named _mini-ndn_ in your home directory, containing all the source code.

Still in your home directory, use the utility install script with _-fnv_ options:

    sudo ./mini-ndn/util/install.sh -fnv

where
-f: install open(F)low
-n: install mini(N)et dependencies + core files
-v: install open (V)switch

Prerequisite packages will be downloaded and installed during the process.

### Verification

Once everything is installed, the following command can be issued for verification from the home folder:

    sudo minindn --pingall 50 --ctime 180 mini-ndn/ndn_utils/hyperbolic_conf_file/minindn.caida.conf

where:
--pingall: Will schedule and collect the specified number of pings from each node to every other node
--ctime: Convergence time for NLSR, provide according to the size of the topology

Note: The configuration file contains hyperbolic coordinates but hyperbolic routing will only be
activated if --hr is provided

All the ping logs will be stored under /tmp/node-name/ping-data and the command will provide a
command line interface at the end.
