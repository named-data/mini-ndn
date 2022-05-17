Experiment
==========

Configuration
-------------

Mini-NDN uses a configuration file describing the topology and its parameters to setup a network.

The [nodes] section:

At the bare minimum, the node section describes the nodes present in the
topology.

::

    [nodes]
    a: key1=value1 key2=value2
    b: key1=value1

Any key and value passed here is accessible in Mini-NDN as:

::

    ndn = Minindn(...)
    value = ndn.net.hosts[0].params['params'].get('key1', "defaultValue")

One can specify log levels for each node's NFD and NLSR using this key-value system:

::

    [nodes]
    a: nfd-log-level=DEBUG nlsr-log-level=DEBUG
    b: nfd-log-level=INFO

To specify a log level for certain modules of NFD, the following line can be added to `nfd.py`:

::

   node.cmd('infoedit -f {} -s log.Forwarder -v {}'.format(self.confFile, 'INFO'))

This will turn on FORWARDER logging to INFO for all nodes.

.. Todo: Add switch section

The [links] section:

The links section describes the links in the topology.

::

    e.g.)

    [links]
    a:b delay=10ms

This would create a link between a and b. 'b:a' would also result in the
same. The following parameters can be configured for a node:

-  delay : Delay parameter is a required parameter which defines the
   delay of the link (1-1000ms)

-  bw : Bandwidth of a link (<1-1000> Mbps)

-  loss : Percentage of packet loss (<1-100>)

Example configuration file

::

    [nodes]
    a:
    b:
    [links]
    a:b delay=10ms bw=100

See ``ndn_utils/topologies`` for more sample files

Sample
------

Sample experiment may written as follows:

.. code:: python

    from mininet.log import setLogLevel, info

    from minindn.minindn import Minindn
    from minindn.util import MiniNDNCLI
    from minindn.apps.appmanager import AppManager
    from minindn.apps.nfd import Nfd
    from minindn.apps.nlsr import Nlsr
    from minindn.helpers.routing_helper import IPRoutingHelper

    if __name__ == '__main__':
        setLogLevel('info')

        Minindn.cleanUp()
        Minindn.verifyDependencies()

        # Can pass a custom parser, custom topology, or any Mininet params here
        ndn = Minindn()

        ndn.start()

        # IP reachability if needed
        # IPRoutingHelper.calcAllRoutes(ndn.net)
        # info("IP routes configured, start ping\n")
        # ndn.net.pingAll()

        # Start apps with AppManager which registers a clean up function with ndn
        info('Starting NFD on nodes\n')
        nfds = AppManager(ndn, ndn.net.hosts, Nfd)
        info('Starting NLSR on nodes\n')
        nlsrs = AppManager(ndn, ndn.net.hosts, Nlsr)

        # or can not start NLSRs with some delay in between:
        # nlsrs = AppManager(ndn, ndn.net.hosts, Nlsr)
        # for host in ndn.net.hosts:
        #     nlsrs.startOnNode(host)
        #     time.sleep(30)

        MiniNDNCLI(ndn.net)

        # Calls the clean up functions registered via AppManager
        ndn.stop()

Users may look at how the NFD and NLSR applications are written as a sub class of Application
in the ``minindn/apps`` folder. Or users may choose to directly run their application on nodes
such as ndnpingserver is run in ``minindn/helpers/experiment.py``.

**Note:** A certain log-level can be set-up for all the NFD or NLSR nodes at once by passing it as an argument during the startup.

``nfds = AppManager(self.ndn, self.ndn.net.hosts, Nfd, logLevel='DEBUG')`` (same for NLSR)

Execution
---------

To run Mini-NDN with the default topology,
``ndn_utils/topologies/default-topology.conf``, type:

::

    sudo python examples/minindn.py

To run Mini-NDN with a topology file, provide the filename as the first
argument:

::

    sudo python examples/minindn.py my-topology.conf

After Mini-NDN is installed, users can run examples from anywhere with python directly as follows:

::

    sudo python /path/to/myexample.py

The user no longer needs to create an experiment in the old Mini-NDN way, then install it to the system before executing it via the minindn binary. The new examples can be separate from the Mini-NDN folder if the core is not being modified.

CLI Interface
_____________

During set up, the list of nodes in the network will be listed as they
are initialized:

::

    *** Adding hosts:
    a b c d

After set up, the command-line interface (CLI) will display a prompt.

::

    mini-ndn>

To interact with a node, first type the node's name and then the command
to be executed:

::

    mini-ndn> a echo "Hello, world!"
    Hello, world!

To see the status of the forwarder on the node:

::

    mini-ndn> a nfdc status report

To see the status of routing on the node:

::

    mini-ndn> a nlsrc status

To exit Mini-NDN, type ``quit`` in the CLI or use ``ctrl + D``:

::

    mini-ndn> quit

``Ctrl + C`` is used to quit an application run in the foreground of the command line.

For a more in depth explanation of the CLI, please see the `Mininet
Walkthrough <http://mininet.org/walkthrough/>`__.

To run NDN commands from the outside the command line user can also open a new terminal
and export the HOME folder of a node ``export HOME=/tmp/minindn/a && cd ~``

Working Directory Structure
---------------------------

Currently Mini-NDN uses /tmp/minindn as the working directory if not
specified otherwise by using the option --work-dir.

Each node is given a HOME directory under /tmp/minindn/<node-name> where
<node-name> is the name of the node specified in the [nodes] section of
the conf file.

NFD
___

- NFD conf file is stored at ``/tmp/minindn/<node-name>/nfd.conf``

- NFD log file is stored at ``/tmp/minindn/<node-name>/log/nfd.log``

- ``.ndn`` folder is stored at ``/tmp/minindn/<node-name>/.ndn``

NLSR
____

- NLSR conf file is stored at ``/tmp/minindn/<node-name>/nlsr.conf``
- NLSR log file is stored at ``/tmp/minindn/<node-name>/log/nlsr.log``

When security is enabled, NLSR security certificates are stored in:
``/tmp/minindn/<node-name>/security`` Note that no NLSR publishes the root
certificate, Mini-NDN installs root.cert in security folder for each
NLSR.

While a host's NLSR neighbors are by default populated by adjacent nodes in wired scenarios,
for those running NLSR on wifi stations it is required that you specify "neighbor" faces
manually. The framework for this is provided either via a dictionary object or through
additional sections in topology files, and may also be used for wired experiments.
See an example of a topo of this sort in ``mini-ndn/topologies/wifi/nlsr_wifi_example.conf``.
NLSR faces to be created can be manually specified from topology files in a ``[faces]``
section, with the format ``nodeA:nodeB [cost=X]``. You should then call the ``setupFaces()``
method of an initialized Mini-NDN object to get a dictionary based on this parse in the format
``faceA:[(faceB, cost), (faceC, cost),...]``, which can finally be passed to the NLSR
helper via the faceDict parameter. An example experiment using this methodology is located
at ``mini-ndn/examples/wifi/nlsr_wifi.py``. Note that the aforementioned dict can also be
created manually in the previously established format.

Routing Options
----------------

Link State Routing (NLSR)
_________________________
By default, Mini-NDN uses `NLSR <https://github.com/named-data/NLSR>`__ for route management i.e route computation, route installation and so on. Additionally, the command line utility ``nlsrc`` can be used to advertise and withdraw prefixes and route status.


NDN Routing Helper
____________________
Computes link-state or hyperbolic route/s from a given minindn topology and installs them in the FIB. The major benefit of the routing helper is to eliminate the overhead of NLSR when using larger topology. See ``examples/static_routing_experiment.py`` on how to use the helper class.

**IMPORTANT:** NLSR and NDN Routing Helper are mutually exclusive, meaning you can only use one at a time, not both.

**Note:** The current version of ``ndn_routing_helper`` is still in the experimental phase. It doesn't support node or link failure and runtime prefix advertisement/withdrawal. If you find any bug please report `here <https://redmine.named-data.net/projects/mini-ndn>`__ or contact the :doc:`authors <authors>`.

IP Routing Helper
____________________

The routing helper allows to run IP-based evaluations with Mini-NDN. It configures static IP routes to all nodes, which means that all nodes can reach all other nodes in the network
reachable, even when relaying is required. Please see ``examples/ip_rounting_experiment.py`` for a simple example.
