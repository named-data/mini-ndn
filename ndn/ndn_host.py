from mininet.node import CPULimitedHost, Host, Node
from ndn.nfd import Nfd

class NdnHostCommon():
    "Common methods of NdnHost and CpuLimitedNdnHost"

    def configNdn(self):
        self.buildPeerIp()

    def buildPeerIp(self):
        for iface in self.intfList():
            link = iface.link
            if link:
                node1, node2 = link.intf1.node, link.intf2.node
                if node1 == self:
                    self.peerList[node2.name] = link.intf2.node.IP(link.intf2)
                else:
                    self.peerList[node1.name] = link.intf1.node.IP(link.intf1)

    inited = False

    @classmethod
    def init(cls):
        "Initialization for NDNHost class"
        cls.inited = True

class NdnHost(Host, NdnHostCommon):
    "NDNHost is a Host that always runs NFD"

    def __init__(self, name, **kwargs):

        Host.__init__(self, name, **kwargs)
        if not NdnHost.inited:
            NdnHostCommon.init()

        self.nfd = Nfd(self)
        self.nfd.start()

        self.peerList = {}

    def config(self, fib=None, app=None, cache=None, **params):

        r = Node.config(self, **params)

        self.setParam(r, 'app', fib=fib)   # why is this not app=app, to be investigated
        self.setParam(r, 'fib', app=app)   # and this fib=fib
        self.setParam(r, 'cache', cache=cache)

        return r

    def terminate(self):
        "Stop node."
        self.nfd.stop()
        Host.terminate(self)

class CpuLimitedNdnHost(CPULimitedHost, NdnHostCommon):
    '''CPULimitedNDNHost is a Host that always runs NFD and extends CPULimitedHost.
       It should be used when one wants to limit the resources of NDN routers and hosts '''

    def __init__(self, name, sched='cfs', **kwargs):

        CPULimitedHost.__init__(self, name, sched, **kwargs)
        if not NdnHost.inited:
            NdnHostCommon.init()

        self.nfd = Nfd(self)
        self.nfd.start()

        self.peerList = {}

    def config(self, fib=None, app=None, cpu=None, cores=None, cache=None, **params):

        r = CPULimitedHost.config(self,cpu,cores, **params)

        self.setParam(r, 'app', fib=fib)   #????? shoud it be app=app
        self.setParam(r, 'fib', app=app)
        self.setParam(r, 'cache', cache=cache)

        return r

    def terminate(self):
        "Stop node."
        self.nfd.stop()
        Host.terminate(self)
