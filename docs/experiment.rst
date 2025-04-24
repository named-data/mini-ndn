Experiment
==========

Configuration
-------------

Mini-NDN uses a configuration file describing the topology and its parameters to setup a network.

**The [nodes] section**

At the bare minimum, the ``nodes`` section describes the nodes present in the
topology, e.g.:

.. code-block:: cfg

    [nodes]
    a: key1=value1 key2=value2
    b: key1=value1

Any key and value passed here is accessible in Mini-NDN as:

.. code-block:: python

    ndn = Minindn(...)
    value = ndn.net.hosts[0].params['params'].get('key1', 'defaultValue')

One can specify log levels for each node's NFD and NLSR using this key-value system:

.. code-block:: cfg

    [nodes]
    a: nfd-log-level=DEBUG nlsr-log-level=DEBUG
    b: nfd-log-level=INFO

To specify a log level for certain modules of NFD, the following line can be added to ``nfd.py``:

.. code-block:: python

   node.cmd('infoedit -f {} -s log.Forwarder -v {}'.format(self.confFile, 'INFO'))

This will turn on Forwarder logging to INFO for all nodes.

.. todo::
    Document [switches] section

**The [links] section**

The ``links`` section describes the links in the topology, e.g.:

.. code-block:: cfg

    [links]
    a:b delay=10ms

This would create a link between a and b. 'b:a' would also result in the
same. The following parameters can be configured for a node:

-  ``delay`` : Delay parameter is a required parameter which defines the
   delay of the link (1-1000ms)

-  ``bw`` : Bandwidth of a link (<1-1000> Mbps)

-  ``loss`` : Percentage of packet loss (<1-100>)

Example configuration file:

.. code-block:: cfg

    [nodes]
    a:
    b:
    [links]
    a:b delay=10ms bw=100

See the ``topologies`` folder for more sample files.

Example
-------

Sample experiment may written as follows:

.. code-block:: python

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

**Note:** A certain log level can be configured for all the NFD or NLSR nodes at once by passing it as an argument during startup, e.g.:

.. code-block:: python

    nfds = AppManager(self.ndn, self.ndn.net.hosts, Nfd, logLevel='DEBUG')

Execution
---------

To run Mini-NDN with the default topology, ``topologies/default-topology.conf``, type:

.. code-block:: sh

    sudo python examples/minindn.py

To run Mini-NDN with a topology file, provide the filename as the first
argument:

.. code-block:: sh

    sudo python examples/minindn.py my-topology.conf

After Mini-NDN is installed, users can run examples from anywhere with python directly as follows:

.. code-block:: sh

    sudo python /path/to/myexample.py

The user no longer needs to create an experiment in the old Mini-NDN way, then install it to the system before executing it via the minindn binary. The new examples can be separate from the Mini-NDN folder if the core is not being modified.

CLI Interface
_____________

During set up, the list of nodes in the network will be listed as they
are initialized:

.. code-block:: none

    *** Adding hosts:
    a b c d

After set up, the command-line interface (CLI) will display a prompt.

.. code-block:: none

    mini-ndn>

To interact with a node, first type the node's name and then the command
to be executed:

.. code-block:: sh

    mini-ndn> a echo "Hello, world!"
    Hello, world!

To see the status of the forwarder on the node:

.. code-block:: sh

    mini-ndn> a nfdc status report

To see the status of routing on the node:

.. code-block:: sh

    mini-ndn> a nlsrc status

To exit Mini-NDN, type ``quit`` in the CLI or use :kbd:`Ctrl-d`:

.. code-block:: sh

    mini-ndn> quit

:kbd:`Ctrl-c` is used to quit an application run in the foreground of the command line.

For a more in depth explanation of the CLI, please see the `Mininet
Walkthrough <https://mininet.org/walkthrough/>`__.

To run NDN commands from the outside the command line user can also open a new terminal
and export the HOME folder of a node:

.. code-block:: sh

    export HOME=/tmp/minindn/a && cd ~

GUI Interface
--------------
Mini-NDN provides an optional browser-based GUI interface via `NDN-Play <https://github.com/pulsejet/ndn-play>`__.

An example can be found at ``examples/ndn_play_demo.py``. To start the server, add the following to your Mininet script.
This will print the URL of the server.

.. code-block:: python

    from minindn.minindn_play.server import PlayServer

    if __name__ == '__main__':
        # placeholder
        PlayServer(net).start() # starts the server and blocks

If running remotely, you must make sure to forward the port 8765 to the local
machine where the browser is running (this port is used by the websocket server). Remember that Mini-NDN runs with superuser
privileges, so do this judiciously.

Wireshark Visualization
_______________________

MiniNDN stores the ``hosts.params['params']['homeDir']`` variable for all hosts, used to identify the home directory of the
nodes. The wireshark dump must be stored in ``shark.log`` in the ``<node-home>/log`` directory for each node. Using the app
manager, this can be done as,

.. code-block:: python

    from minindn.apps.app_manager import AppManager
    from minindn.apps.tshark import Tshark

    if __name__ == '__main__':
        # placeholder
        ndn.initParams(ndn.net.hosts)
        sharks = AppManager(ndn, ndn.net.hosts, Tshark, singleLogFile=True)

Once setup, the dump will be visible for each node and the TLV inspector will show each packet on double-clicking it in the GUI.
If this fails to function, we recommending following the troubleshooting steps for the `NDN Wireshark Dissector
<https://github.com/named-data/ndn-tools/blob/master/tools/dissect-wireshark/README.md>`__ before filing an issue.

Log Monitor
___________

The log monitor periodically captures the output of one or more log files on each node and shows the events on the topology
visually by changing the color of the node. In the following example, the `log/my_app.log` at each host will be monitored
every `200ms`, for all lines (matching the regex `.*`).

.. code-block:: python

    from minindn.minindn_play.monitor import LogMonitor

    if __name__ == '__main__':
        ...

        server = PlayServer(net)
        server.add_monitor(LogMonitor(net.hosts, "log/my_app.log", interval=0.2, regex_filter=".*"))
        server.start()


Working Directory Structure
---------------------------

Currently Mini-NDN uses ``/tmp/minindn`` as the working directory if not
specified otherwise by using the option ``--work-dir``.

Each node is given a HOME directory under ``/tmp/minindn/<node-name>`` where
``<node-name>`` is the name of the node specified in the ``[nodes]`` section of
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

By default, Mini-NDN uses `NLSR <https://github.com/named-data/NLSR>`__ for route management, i.e., route computation, route installation, etc.
Additionally, the command-line utility ``nlsrc`` can be used to advertise and withdraw prefixes and route status.

NDN Routing Helper
__________________

Computes link-state or hyperbolic route/s from a given minindn topology and installs them in the FIB. The major benefit of the routing helper is to eliminate the overhead of NLSR when using larger topology. See ``examples/static_routing_experiment.py`` on how to use the helper class.

**IMPORTANT:** NLSR and NDN Routing Helper are mutually exclusive, meaning you can only use one at a time, not both.

**Note:** The current version of ``ndn_routing_helper`` is still in the experimental phase. It doesn't support node or link failure and runtime prefix advertisement/withdrawal. If you find any bug please report `here <https://redmine.named-data.net/projects/mini-ndn>`__ or contact the :doc:`authors <authors>`.

IP Routing Helper
____________________

The routing helper allows to run IP-based evaluations with Mini-NDN. It configures static IP routes to all nodes, which means that all nodes can reach all other nodes in the network
reachable, even when relaying is required. Please see ``examples/ip_rounting_experiment.py`` for a simple example.
