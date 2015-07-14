Getting Started
===============

## Installation
Please see [INSTALL.md](../INSTALL.md) for instructions on installing Mini-NDN and its dependencies.

## Running Mini-NDN

To run Mini-NDN with the default topology, ``ndn_utils/topologies/default-topology.conf``, type:

    sudo minindn

To run Mini-NDN with a topology file, provide the filename as the first argument:

    sudo minindn my-topology.conf

During set up, the list of nodes in the network will be listed as they are initialized:

    *** Adding hosts:
    a b c d

After set up, the command-line interface (CLI) will display a prompt.

    mininet>

To interact with a node, first type the node's name and then the command to be executed:

    mininet> a echo "Hello, world!"
    Hello, world!

To see the status of the forwarder on the node:

    mininet> a nfd-status

To see the status of routing on the node:

    mininet> a nlsrc status

To exit Mini-NDN, type ``quit`` in the CLI:

    mininet> quit

For a more in depth explanation of the CLI, please see the
[Mininet Walkthrough](http://mininet.org/walkthrough/).

## Command-line options

To run Mini-NDN with a replica of the NDN testbed, use the ``--testbed`` parameter:

    sudo mini-ndn --testbed

#### Routing options

To run NLSR with hyperbolic routing enabled, use the ``--hr`` parameter:

    sudo mini-ndn --hr

To configure the max number of faces added by NLSR to reach each name prefix, use the ``--faces``
parameter:

    sudo mini-ndn --faces 3

``--faces`` can be an integer from 0 to 60; 0 indicates NLSR can add all available faces.


