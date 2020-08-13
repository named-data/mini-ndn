Howtos
======

Connect Mini-NDN nodes to an outside network
---------------------------------------------

Mini-NDN nodes can be connected to an outside network indirectly by
running NFD on the local machine:

::

    (Mini-NDN node) ------ (NFD running on the host machine where Mini-NDN is running) ------- (External Network)

Add a node in root namespace
____________________________

For this simple example, we can use a single node topology with node 'a'

If we want node 'a' to connect to the host machine, we need to add a
"root" node which has a link with node "a."

Then the following code can be used:

.. code:: python

    topo = Topo()
    root = topo.addHost('root', inNamespace=False)
    a = topo.addHost('a')
    topo.addLink(root, a, delay='10ms')

    ndn = Minindn(topo=topo)

    ...

Configuration
_____________

Run Mini-NDN with the above code and issue ifconfig on the local
machine to confirm the addition of the interface. You should be able to
locate "root-eth0":

::

    root-eth0 Link encap:Ethernet  HWaddr 3e:eb:77:d2:6f:1f
              inet addr:1.0.0.9  Bcast:1.0.0.11  Mask:255.255.255.252
              inet6 addr: fe80::3ceb:77ff:fed2:6f1f/64 Scope:Link
              UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
              RX packets:34 errors:0 dropped:0 overruns:0 frame:0
              TX packets:33 errors:0 dropped:0 overruns:0 carrier:0
              collisions:0 txqueuelen:1000
              RX bytes:2667 (2.6 KB)  TX bytes:2797 (2.7 KB)

To make the IP address associated with this interface persistent, add
the following line to /etc/network/interfaces and reboot your machine:

::

    iface root-eth0 inet manual

Check connection
________________

After rebooting, run Mini-NDN and issue the following command:

::

    mini-ndn>net
    a a-eth0:b-eth0 a-eth1:c-eth0 a-eth2:root-eth0

Node "a" is connected to "root-eth0". Now issue "ifconfig a-eth2" on
node "a":

::

    mini-ndn>a ifconfig a-eth2
    a-eth2    Link encap:Ethernet  HWaddr fa:76:d4:86:d3:ba
              inet addr:1.0.0.10  Bcast:1.0.0.11  Mask:255.255.255.252

As learned from the previous step, the IP address of root-eth0 is
1.0.0.9.

::

    mini-ndn>a ping 1.0.0.9
    PING 1.0.0.9 (1.0.0.9) 56(84) bytes of data.
    64 bytes from 1.0.0.9: icmp_seq=1 ttl=64 time=0.137 ms
    64 bytes from 1.0.0.9: icmp_seq=2 ttl=64 time=0.123 ms

The host machine will also be able to ping node "a":

::

    VirtualBox:~$ ping 1.0.0.10
    PING 1.0.0.10 (1.0.0.10) 56(84) bytes of data.
    64 bytes from 1.0.0.10: icmp_seq=1 ttl=64 time=0.086 ms

Run NFD on local machine and register route
___________________________________________

Start NFD on the local machine by using:

::

    sudo nfd

The "nfd-start" script cannot be used, since the script allows only one
instance of NFD at a time. The NFD processes running on the Mini-NDN
nodes will prevent the "nfd-start" script from working.

Now, using "nfdc register", we can register a route from node "a" in
Mini-NDN to the NFD process on the host machine and from the host
machine to an external machine.

Also, if the local machine has a public IP, Mini-NDN nodes can be
reached via external machines.

Generate NDN testbed topology
___________________________________________

Run the following install.sh command

::

    python3 util/testbed_topo_generator.py

This will place a "testbed.conf" file in the topologies subdirectory,
where it can be referenced as desired. To update the topology, simply
rerun this command.