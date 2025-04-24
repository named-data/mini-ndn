import re
from time import sleep
from io import TextIOWrapper
from threading import Thread

import msgpack

from mininet.node import Node
from minindn.util import host_home
from minindn.minindn_play.socket import PlaySocket
from minindn.minindn_play.consts import WSKeys, WSFunctions


class LogMonitor:
    nodes: list[Node]
    log_file: str
    interval: float
    socket: PlaySocket
    filter: re.Pattern
    quit: bool = False

    def __init__(self, nodes: list, log_file: str, interval: float = 0.5, regex_filter: str = ''):
        self.nodes = nodes
        self.log_file = log_file
        self.interval = interval
        self.regex_filter = re.compile(regex_filter)

    def start(self, socket: PlaySocket):
        self.socket = socket
        Thread(target=self._start).start()

    def stop(self):
        self.quit = True

    def _start(self):
        files: list[TextIOWrapper] = []
        counts: dict[str, int] = {}

        for node in self.nodes:
            path = f"{host_home(node)}/{self.log_file}"
            files.append(open(path, 'r'))
            counts[node.name] = 0

        while not self.quit:
            for i, file in enumerate(files):
                node = self.nodes[i]
                counts[node.name] = 0
                while line := file.readline():
                    if self.regex_filter.match(line):
                        counts[node.name] += 1

            self._send(counts)
            sleep(self.interval)

        for file in files:
            file.close()

    def _send(self, counts: dict[str, int]):
        self.socket.send_all(msgpack.dumps({
            WSKeys.MSG_KEY_FUN: WSFunctions.MONITOR_COUNTS,
            WSKeys.MSG_KEY_RESULT: counts,
        }))
