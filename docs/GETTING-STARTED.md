Getting Started
===============

## Installation
Please see [INSTALL.md](../INSTALL.md) for instructions on installing MiniNDN-WiFi and its dependencies.

## Running MiniNDN-WiFi

In MiniNDN-WiFi, We can emulate a wireless network with Access Points (APs), ad hoc network or mobile ad hoc network.

We can use the two default configuration file for topology in directory ndnwifi_utils/topologies/: `singleap-topology.conf`, 'adhoc-topology.conf'. We can also use customized topology.

Based on the two topology file, a WiFI network with one AP, ad hoc network or mobile ad hoc network will be created when you type the following command: 

    sudo minindn --wifi [--adhoc] [--manet] 
    
A full list of other options can be printed by using:

    sudo minindn --wifi --help

To run MiniNDN-WiFi with a customized topology file, provide the filename as the first argument:

    sudo minindn --wifi my-topology.conf

During set up, the list of nodes in the network will be listed as they are initialized:

*** Adding hosts and stations:

sta1 sta2 sta3 sta4

After set up, the command-line interface (CLI) will display a prompt.

    minindn-wifi>

To interact with a node, first type the node's name and then the command to be executed:

    minindn-wifi> sta1 echo "Hello, world!"
    Hello, world!

To see the status of the forwarder NFD on the node:

    minindn-wifi> sta1 nfdc status report

Assume that we have created an ad hoc network with 4 nodes. We can use NDN's tools to test running. Please see the detail explanation [ndn-tools] (https://github.com/named-data/ndn-tools)

To move a node to the specified posit

To exit MiniNDN-WiFi, type `quit` in the CLI:

    minindn-wifi> quit

For a more in depth explanation of the CLI, please see the
[Mininet Walkthrough](http://mininet.org/walkthrough/).

## Command-line options

To run Mini-NDN with a replica of the NDN testbed, use the `--testbed` parameter:

    sudo minindn --testbed

To change the working directory from default `/tmp` following option can be used:

    sudo minindn --work-dir /home/mydir/test

#### Routing options

To run NLSR with hyperbolic routing enabled, use the `--hr` parameter:

    sudo minindn --hr

Topology files given under ndn_utils/topologies/minindn* have hyperbolic coordinates configured and can be used with this option.

To configure the max number of faces added by NLSR to reach each name prefix, use the `--faces`
parameter:

    sudo minindn --faces 3

`--faces` can be an integer from 0 to 60; 0 indicates NLSR can add all available faces.

To run Mini-NDN with NLSR security configured

    sudo minindn --nlsr-security

## Working Directory Structure

Currently Mini-NDN uses /tmp as the working directory if not specified otherwise by using the option --work-dir.

Each node is given a HOME directory under /tmp/node-name
where node-name is the name of the node specified in the [nodes] section of the conf file.

### NFD
NFD conf file is stored at `/tmp/node-name/node-name.conf`

NFD log file is stored at `/tmp/node-name/node-name.log`

`.ndn` folder is stored at `/tmp/node-name/.ndn`

### NLSR
NLSR conf file is stored at `/tmp/node-name/nlsr.conf`

NLSR log file is stored at `/tmp/node-name/log/nlsr.log`

When security is enabled, NLSR security certificates are stored in: `/tmp/node-name/security`
Note that no NLSR publishes the root certificate, Mini-NDN installs root.cert in security folder for each NLSR.
