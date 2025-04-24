import signal
from threading import Thread

from mininet.net import Mininet
from minindn.minindn_play.monitor import LogMonitor
from minindn.minindn_play.socket import PlaySocket
from minindn.minindn_play.net.topo import TopoExecutor
from minindn.minindn_play.net.state import StateExecutor
from minindn.minindn_play.term.term import TermExecutor
from minindn.minindn_play.shark.shark import SharkExecutor

class PlayServer:
    net: Mininet
    repl: bool
    cli: bool
    monitors: list[LogMonitor] = []

    def __init__(self, net: Mininet, **kwargs) -> None:
        """
        Start NDN Play GUI server.
        If cli=True is specified (default), will block for the Mininet CLI.
        """

        self.net = net
        self.repl = kwargs.get('repl', False)
        self.cli = kwargs.get('cli', True)

        self.socket = PlaySocket()
        self.socket.add_executor(TopoExecutor(net))
        self.socket.add_executor(StateExecutor(net))

        self.shark_executor = SharkExecutor(net, self.socket)
        self.socket.add_executor(self.shark_executor)

        self.pty_executor = TermExecutor(net, self.socket)
        self.socket.add_executor(self.pty_executor)

    def start(self):
        if self.repl:
            Thread(target=self.pty_executor.start_repl).start()

        # Start all monitors
        for monitor in self.monitors:
            monitor.start(self.socket)

        # Blocks until Mininet CLI is closed
        if self.cli:
            self.hook_sigint()
            self.pty_executor.start_cli()

        # Stop all monitors
        for monitor in self.monitors:
            monitor.stop()

    def hook_sigint(self):
        def signal_handler(sig, frame):
            print('SIGINT received, stopping Mininet...')
            self.net.stop()
            exit(127)
        signal.signal(signal.SIGINT, signal_handler)

    def add_monitor(self, monitor: LogMonitor):
        self.monitors.append(monitor)
