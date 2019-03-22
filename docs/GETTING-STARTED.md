Getting Started
===============

## Installation
Please see [INSTALL.md](../INSTALL.md) for instructions on installing
MiniNDN-WiFi and its dependencies.

## Running MiniNDN-WiFi

In MiniNDN-WiFi, We can emulate a wireless network with Access Points
(APs), ad hoc network or mobile ad hoc network.

We can use the two default configuration files for topology in
directory ndnwifi_utils/topologies/: `singleap-topology.conf`,
'adhoc-topology.conf'. We can also use customized topology. We can use
vndn-topology.conf when we emulate a ndn-vanet/vndn.

Based on these topology files, a WiFI network with one AP, ad hoc
network or mobile ad hoc network will be created when you type the
following command:

    sudo minindn --wifi [--adhoc] [--manet] [--vndn] [--sumovndn]
    
A full list of other options can be printed by using:

    sudo minindn --wifi --help

To run MiniNDN-WiFi with a customized topology file, provide the
filename as the first argument:

    sudo minindn --wifi my-topology.conf

During set up, the list of nodes in the network will be listed as they
are initialized:

*** Adding hosts and stations:

sta1 sta2 sta3 sta4

After set up, the command-line interface (CLI) will display a prompt.

    minindn-wifi>

To interact with a node, first type the node's name and then the
command to be executed:

    minindn-wifi> sta1 echo "Hello, world!"
    Hello, world!

To see the status of the forwarder on the node:

    minindn-wifi> a nfdc status report

To see the status of routing on the node:

    minindn-wifi> a nlsrc status

To exit Mini-NDN, type `quit` in the CLI:

    minindn-wifi> quit

Another option to quit Mini-NDN is sending a SIGQUIT (ctrl+\). SIGINT
(ctrl+c) is reserved for the purpose of stopping applications
initiated on the minindn command line.

For a more in depth explanation of the CLI, please see the
[Mininet Walkthrough](http://mininet.org/walkthrough/).

## Command-line options

To run Mini-NDN with a replica of the NDN testbed, use the
`--testbed` parameter:

    sudo minindn --testbed

To change the working directory from default `/tmp/minindn` following
option can be used:

    sudo minindn --work-dir /home/mydir/test

<<<<<<< HEAD
Autocomplete of command-line options is available for users of Bash and Zsh.
=======
Assume that we have created an ad hoc network with 4 nodes. We can use
NDN's tools and mininet-wifi CLI command to test running. Please see
the detail explanations:

   [ndn-tools] (https://github.com/named-data/ndn-tools)
   
   [mininet-wifi] (https://github.com/intrig-unicamp/mininet-wifi)

To move a node to the specified position, we can use 'py', for example:

    minindn-wifi> py sta1.setPosition('10,40,0')

Assume that the node sta4 is a content producer, to generate a content
with name "hello", we can use "ndnpoke":

    minindn-wifi>sta4 echo "hello world" | ndnpoke -w 3000 /hello &
    
If the node sta1 hope to retrive the content provided by sta4 and need
the node sta2 to forward the interest packet to the node sta4, we can
use the following command to add a route that point to the prefix
"hello" on sta1 and sta2.

    minindn-wifi>sta1 nfdc route add /hello 257
    
    minindn-wifi>sta2 nfdc route add /hello 257
    
To send an interest packet, we can use the command 'ndnpeek'.

    minindn-wifi> sta1 ndnpeek -p /hello
    
To exit MiniNDN-WiFi, type `quit` in the CLI:

    minindn-wifi> quit

Currently Mini-NDN uses /tmp/minindn as the working directory if not
specified otherwise by using the option --work-dir.

Each node is given a HOME directory under /tmp/minindn/node-name where
node-name is the name of the node specified in the [nodes] section of
the conf file.

>>>>>>> wifi

#### Routing options

You probably don't want this, since NLSR does not work correctly with
broadcast links. If you have a topology that mixes wireless and wired
sections, you may want to enable NLSR routing for the wired sections,
however.

To run Mini-NDN Wifi with NLSR, use the `--nlsr` parameter:

    sudo minindn --nlsr
    
To run NLSR with hyperbolic routing enabled, use the `--routing` parameter:

    sudo minindn --nlsr --routing hr

Topology files given under ndn_utils/topologies/minindn* have
hyperbolic coordinates configured and can be used with this option.

To run NLSR in dry-run mode, use the `--routing` parameter:

    sudo minindn --nlsr --routing dry

To configure the max number of faces added by NLSR to reach each name
prefix, use the `--faces` parameter:

    sudo minindn --nlsr --faces 3

`--faces` can be an integer from 0 to 60; 0 indicates NLSR can add all
available faces.

To run Mini-NDN with NLSR security configured

    minindn-wifi> sta1 nfdc status report

### NFD
NFD conf file is stored at `/tmp/minindn/node-name/node-name.conf`

NFD log file is stored at `/tmp/minindn/node-name/node-name.log`

`.ndn` folder is stored at `/tmp/minindn/node-name/.ndn`

### NLSR
NLSR conf file is stored at `/tmp/minindn/node-name/nlsr.conf`

NLSR log file is stored at `/tmp/minindn/node-name/log/nlsr.log`

When security is enabled, NLSR security certificates are stored in: `/tmp/minindn/node-name/security`
Note that no NLSR publishes the root certificate, Mini-NDN installs root.cert in security folder for each NLSR.
