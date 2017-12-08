Getting Started
===============

## Installation
Please see [INSTALL.md](../INSTALL.md) for instructions on installing MiniNDN-WiFi and its dependencies.

## Running MiniNDN-WiFi

In MiniNDN-WiFi, We can emulate a wireless network with Access Points (APs), ad hoc network or mobile ad hoc network.

We can use the two default configuration files for topology in directory ndnwifi_utils/topologies/: `singleap-topology.conf`, 'adhoc-topology.conf'. We can also use customized topology. We can use vndn-topology.conf when we emulate a ndn-vanet/vndn.

Based on these topology files, a WiFI network with one AP, ad hoc network or mobile ad hoc network will be created when you type the following command: 

    sudo minindn --wifi [--adhoc] [--manet] [--vndn] [--sumovndn]
    
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

Assume that we have created an ad hoc network with 4 nodes. We can use NDN's tools and mininet-wifi CLI command to test running. Please see the detail explanations:

   [ndn-tools] (https://github.com/named-data/ndn-tools)
   
   [mininet-wifi] (https://github.com/intrig-unicamp/mininet-wifi)

To move a node to the specified position, we can use 'py', for example:

    minindn-wifi> py sta1.setPosition('10,40,0')

Assume that the node sta4 is a content producer, to generate a content with name "hello", we can use "ndnpoke":

    minindn-wifi>sta4 echo "hello world" | ndnpoke -w 3000 /hello &
    
If the node sta1 hope to retrive the content provided by sta4 and need the node sta2 to forward the interest packet to the node sta4, we can use the following command to add a route that point to the prefix "hello" on sta1 and sta2.

    minindn-wifi>sta1 nfdc route add /hello 257
    
    minindn-wifi>sta2 nfdc route add /hello 257
    
To send an interest packet, we can use the command 'ndnpeek'.

    minindn-wifi> sta1 ndnpeek -p /hello
    
To exit MiniNDN-WiFi, type `quit` in the CLI:

    minindn-wifi> quit
