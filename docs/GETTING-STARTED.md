Getting Started
===============

## Installation
Please see [INSTALL.md](../INSTALL.md) for instructions on installing Mini-NDN and its dependencies.

## Running Mini-NDN

To run Mini-NDN with the default topology, `ndn_utils/topologies/default-topology.conf`, type:

    sudo minindn

A full list of options can be printed by using:

    sudo minindn --help

To run Mini-NDN with a topology file, provide the filename as the first argument:

    sudo minindn my-topology.conf

During set up, the list of nodes in the network will be listed as they are initialized:

    *** Adding hosts:
    a b c d

After set up, the command-line interface (CLI) will display a prompt.

    mini-ndn>

To interact with a node, first type the node's name and then the command to be executed:

    mini-ndn> a echo "Hello, world!"
    Hello, world!

To see the status of the forwarder on the node:

    mini-ndn> a nfdc status report

To see the status of routing on the node:

    mini-ndn> a nlsrc status

To exit Mini-NDN, type `quit` in the CLI:

    mini-ndn> quit

Another option to quit Mini-NDN is sending a SIGQUIT (ctrl+\). SIGINT (ctrl+c)
is reserved for the purpose of stopping applications initiated on the minindn command
line.

For a more in depth explanation of the CLI, please see the
[Mininet Walkthrough](http://mininet.org/walkthrough/).

## Command-line options

To run Mini-NDN with a replica of the NDN testbed, use the `--testbed` parameter:

    sudo minindn --testbed

To change the working directory from default `/tmp` following option can be used:

    sudo minindn --work-dir /home/mydir/test

#### Routing options

To run minindn without NLSR, use the `--no-nlsr` parameter:

    sudo minindn --no-nlsr

To run NLSR with hyperbolic routing enabled, use the `--routing` parameter:

    sudo minindn --routing hr

Topology files given under ndn_utils/topologies/minindn* have hyperbolic coordinates configured
and can be used with this option.

To run NLSR in dry-run mode, use the `--routing` parameter:

    sudo minindn --routing dry

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
