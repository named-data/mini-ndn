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
    ndn = Minindn(topo=topo)
    ndn.start()
    info("Configuring NFD\n")
    nfds = AppManager(ndn, ndn.net.hosts, Nfd, logLevel="DEBUG")
    #nlsr = AppManager(ndn, ndn.net.hosts, Nlsr, logLevel="DEBUG")
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
    info("Starting pings...\n")
    pingserver_log = open("/tmp/minindn/c/ndnpingserver.log", "w")
    pingserver = getPopen(ndn.net["c"], "ndnpingserver {}".format(PREFIX), stdout=pingserver_log, stderr=pingserver_log)
    ping1 = getPopen(ndn.net["a"], "ndnping {} -c 5".format(PREFIX), stdout=PIPE, stderr=PIPE)
    ping1.wait()
    info(ping1.stdout.read())
    interface = ndn.net["b"].connectionsTo(ndn.net["a"])[0][0]
    info("Failing link\n")
    interface.config(delay="10ms", bw=10, loss=100)
    ping2 = getPopen(ndn.net["a"], "ndnping {} -c 5".format(PREFIX), stdout=PIPE, stderr=PIPE)
    ping2.wait()
    info(ping2.stdout.read())
    interface.config(delay="10ms", bw=10, loss=0)
    MiniNDNCLI(ndn.net)
    info("Finished!\n")
    ndn.stop()

if __name__ == '__main__':
    setLogLevel("info")
    run()
