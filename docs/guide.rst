Getting Started with Writing Mini-NDN Experiments
====
Introduction
=====
When we talk about Mini-NDN, we are referring to what effectively is a library built on top of the Mininet software library. This fact was formerly obfuscated- in its original design, Mini-NDN was a software wrapper that automated and obscured the low-level tasks involved in running Mininet with a combination of input configuration files and dynamically importing user code. While there were benefits to this design, this also fundamentally created what amounted to write-only code for new users and a recurring maintenance and feature addition nightmare- not being able to interact with the low-level API without modifying the main executable was eventually deemed not worth the convenience.
While we have our utility methods and handlers for NDN materials, fundamentally the current backend is pure Mininet. As such, it behooves us to understand how to use this API so we can benefit from our software.
Mininet’s object-oriented design leads us to have to define a few nouns so we have a shared vocabulary:
* Host- A host is, as expected, a network node that is capable of running programs. In implementation, hosts are a network namespace, which is basically a form of low-level container which maintains a separate network stack and isolated processes. Hosts are generally connected by at least one ethernet link via a switch or directly to another node.
* Station- A station is a host with a wifi interface and the capability for mobility. Simulation of wireless links is done via mac80211_hwsim, which is transparent to the stations which simply have normal wlan interfaces.
Stations are Hosts, but not all Hosts are Stations
* Link- A link is an abstraction for a connection between two nodes or a node and an AP/switch specifically. Links generally have two interfaces associated with them which are able to be referenced from the link itself, but wifi to AP links only have one as the other end is the virtual "wireless medium."
* Interface- An interface is an abstraction of a network interface on a host or station. Interfaces provide an API to change their IP, get their name, and other useful utility functions.
* Switch- Implemented via Open-VSwitch, these should behave like normal switches. These are able to be controlled via SDN using a Controller object, which is discussed in the Mininet documentation more extensively than it is here. All switches run in the root userspace.
* AP- An AP is an OVS switch connected to the virtual wireless medium provided by mac80211_hwsim. APs are Switches, not all Switches are APs. APs are able to route based on IP.
* Topo- A Topo object is a representation of a topology that is accepted by a Net object. Topos are used to defined a topology before network creation in the API, though it can be altered or initialized afterwards in some cases. 
* Net- A Net object is effectively a handler for all the stations and connections, and manages starting and stopping the network simulation. It is also the main way of retrieving node objects, as they can be referenced by name in a manner similar to Python dictionaries.

Now, there are a couple things to note after reading this:
* Because switches and APs aren’t isolated like hosts are, NDN routers need to also have a node either connected to a switch with a instantaneous link, or need to be a host with routes manually configured rather than a switch/AP. Which to do is left to the reader’s needs.
* Stations can have wired and wireless interfaces, but typically wired interfaces will need to be manually configured to be functional. This will be detailed further on.

With these ground-level concepts established, let’s proceed onto writing experiments.

Writing Your First Experiment
=====
Mini-NDN experiments, unlike those done by simulators like NDNSim, are best understood as a set of scripts dictating the behavior of Unix systems and a network at large. In many ways Mini-NDN is similar to shell scripting- each host is transparent to itself being containerized which does allow for running actual release code for NFD and ndn-cxx w/o issue. However, there is necessary setup to make this work.
Firstly, we must establish a topology. While we provide a way of writing and parsing non-Python topology configuration files (see <experiment>), for the sake of example we will write pure Python to avoid abstracting concepts before they are understood.
We first create a Topo object. This object provides addHost, addLink, and addSwitch methods. These are used to set the topology of the network as well as the default state of the links. On the links, we specify bw (bandwidth) and delay (communication time between nodes, ie 1/2 RTT, given as a string in the format "Xms" for an integer value X in ms), which are applied on outgoing packets via tc.
.. code-block:: python
    from mininet.log import setLogLevel, info
    from mininet.topo import Topo
    from minindn.minindn import Minindn
    from minindn.apps.app_manager import AppManager
    from minindn.util import MiniNDNCLI, getPopen
    from minindn.apps.nfd import Nfd
    from minindn.apps.nlsr import Nlsr
    from minindn.helpers.nfdc import Nfdc
    from subprocess import PIPE

    PREFIX = "/example"

    def run():
        Minindn.cleanUp()
        Minindn.verifyDependencies()
        topo = Topo()
        # Setup topo
        info("Setup\n")
        a = topo.addHost('a')
        b = topo.addHost('b')
        c = topo.addHost('c')
        topo.addLink(a, b, delay='10ms', bw=10)
        topo.addLink(b, c, delay='10ms', bw=10)

We now must create a network object. Rather than use the default Mininet one, we instead use the provided Minindn object, which is a wrapper that provides utility features to enable NDN support.
.. code:: python

    ndn = Minindn(topo=topo)
    ndn.start()
   
This brings up the containers and network emulation, which lets us begin running apps.
We provide helper methods for running commonly used apps (NFD, NLSR, NFDC, and Tshark [CLI-based Wireshark for capturing pcap files]). In our case, we’ll run NFD, but you can see how to run NLSR here.
.. code:: python
    info("Configuring NFD\n")
    nfds = AppManager(ndn, ndn.net.hosts, Nfd, logLevel="DEBUG")
    #nlsr = AppManager(ndn, ndn.net.hosts, Nlsr, logLevel="DEBUG")


Now we get to the “meat” of our experiment. Mini-NDN provides several ways to interact with our topology, but the main way is via running programs on the respective nodes. Let us try ndnping (If you do not have ndn-tools already, please install it from here[TODO: HYPERLINK]).

First, we need to set up routes between the two nodes using the the provided Nfdc helper. Note that we are able to reference nodes by name from the Net object in a method not dissimilar from a Python dictionary object, this is a very useful tool. Also note that we retrieve the IP from the producer node b’s interface that's connected to the consumer a using `connectionsTo()`. While it's possible to retrieve a node's IP through the `IP()` method, this will only return the address of the first interface of the node and is generally unhelpful.

We can also set the strategy through this same Nfdc API if that is necessary.
.. code:: python
    # This is a fancy way of setting up the routes without violating DRY;
    # the important bit to note is the Nfdc command
    links = {"a":["b"], "b":["c"]}
    for first in links:
        for second in links[first]:
            host1 = ndn.net[first]
            host2 = ndn.net[second]
            interface = host2.connectionsTo(host1)[0][0]
            #info(interface)
            interface_ip = interface.IP()
            Nfdc.createFace(host1, interface_ip)
            Nfdc.registerRoute(host1, PREFIX, interface_ip, cost=0)

Ndnping consists of two components- a consumer and a producer/server. First, we need to start the producer program on the node we choose as the producer, being careful to use a prefix we established previously.

Mini-NDN provides two methods of running CLI programs: either the cmd() method or the getPopen() method. The cmd() method is invoked from hosts and is a blocking method for running commands and returns stdout when finished running. The getPopen() is a wrapper provided from minindn.util and allows a Python Popen object (see subprocess documentation) to be created while maintaining the correct NDN environment variables, which is not inherently blocking and provides far more flexibility in exchange for being moderately more complex to invoke. As the only argument passed to cmd() is the intended shell command, we will instead use Popen for teaching purposes. Note that this wrapper will automatically split commands on spaces, so you don't have to call `split()`, pass `shell=True`, or just write your command as an array yourself.
.. code:: python
    info("Starting pings...\n")
    pingserver_log = open("/tmp/minindn/c/ndnpingserver.log", "w")
    pingserver = getPopen(ndn.net["c"], "ndnpingserver {}".format(PREFIX), stdout=pingserver_log, stderr=pingserver_log)
    ping1 = getPopen(ndn.net["a"], "ndnping {} -c 5".format(PREFIX), stdout=PIPE, stderr=PIPE)
    ping1.wait()
    info(ping1.stdout.read())
Note that you can route stdout and stderr to their relative terminal representations, which will make the output display as normal. However, you can also route these values to a Python file object or the PIPE constant from subprocess. The latter effectively makes it act as a File object in memory with the same API.

We can also tweak link state.

.. code:: python
    interface = ndn.net["b"].connectionsTo(ndn.net["a"])[0][0]
    info("Failing link\n")
    interface.config(delay="10ms", bw=10, loss=100)
    ping2 = getPopen(ndn.net["a"], "ndnping {} -c 5".format(PREFIX), stdout=PIPE, stderr=PIPE)
    ping2.wait()
    info(ping2.stdout.read())
    info("Recovering link\n")
    interface.config(delay="10ms", bw=10, loss=0)
    MiniNDNCLI(ndn.net)
    info("Finished!\n")
    ndn.stop()

    # This is needed to execute the run() method when the script is executed
    if __name__ == '__main__':
        setLogLevel("info")
        run()

We can change the link loss, bandwidth, or several other parameters depending on what network state we want to simulate. A notable quirk of Mininet is that bringing a link fully down destroys the interfaces- as such, it is best to simulate link failure with 100% loss.

We can then print the output of ndnping to stdout for both cases. We should see that the first case received 5/5 data, and the second case received none. Finally, run ndn.stop(), which stops the networks and cleans up the relevant processes.

The Mini-NDN CLI
=====
The Mini-NDN CLI relies primarily on the Mininet CLI. The main usage of it is the fact that it lets you run shell commands on nodes directly- simply use the format
`[node name] [example_command]`
Such as
`c1 nfdc status`.
However, a couple of specific utilities are provided:
??? What does this mean ???
*The most important command is `help`, which will supersede all other commands here
*A wrapper is provided around the `ping` utility, such that you can specify node names instead of IPs. The name will only correspond to the first interface’s IP however, so for topologies with nodes with multiple interfaces you will need to specify the IP.
*The `net` command outputs the structure of the network, which is useful for debugging and validating topologies.
*The `link [host 1] [host 2] [up/down]` command will bring the link between the two specified nodes up or down, which will also destroy their interfaces, so use cautiously.
*You can send commands to the Python interpreter via the `py [command]` command. This is most useful for things like finding a node's position via `py net[node].position` or finding other similar internal values.

While it is likely out of scope to explain the use of common networking utilities to you, the shell utilities `ip` and `tc` are probably the best place to start looking for common tasks, as well as nfdc.

The Mininet-Wifi API and You
=====
Mininet-Wifi is an extension of Mininet geared towards wireless network simulation, especially in regards to mobility. Mininet-Wifi’s mobility simulation is mostly handled behind the scenes, but can be hard to work out how to use or modify if you’re unfamiliar with the source code. 

Mininet-wifi itself runs on wmediumd, a wireless network simulator that applies appropriate wireless signal conditions to mobile stations- signal strength should vary with distance depending on chosen propagation model algorithm (uses log-distance algorithm). 

Mobility simulation is done through predefined algorithms in Mininet-wifi and rendered with Numpy graphs. They can be both 2D and 3D. Mobility behavior is defined in `mn_wifi/mobility.py` in a somewhat obtuse fashion, providing several forms of randomized mobility behavior- you can look at the listed mobility models to see a more specific rundown. There’s also replay mobility, which entails providing sets of start and end coordinates- see the wifi_ping.py class for an example of this in action. This will cause linear movement from the starting to stopping points at specifically given times, with speed calculated from the starting and ending times. There is also VANET (vehicular mobility, using SUMO as a mobility framework rather than Mininet-Wifi's integrated models) simulation, but this will be discussed in a later addition to the documentation.

The `wifi_ping` example located at `mini-ndn/examples/wifi/wifi_ping.py` provides examples of how to invoke both replay and model mobility.