from mininet.net import Mininet
from minindn.util import is_valid_hostid, run_popen

class StateExecutor:
    def __init__(self, net: Mininet):
        self.net = net

    async def get_fib(self, node_id):
        """UI Function: Get the NFDC status report and ifconfig as the fib"""
        if not is_valid_hostid(self.net, node_id):
            if node_id in self.net:
                node = self.net[node_id]
                return { "id": node_id, "fib": f"Node is not a host ({node.__class__.__name__})" }
            return

        node = self.net[node_id]
        nfd_status = run_popen(node, "nfdc status report".split()).decode("utf-8")
        ifconfig = run_popen(node, "ifconfig".split()).decode("utf-8")
        output = nfd_status + "\n" + ifconfig
        return {
            "id": node_id,
            "fib": output,
        }
