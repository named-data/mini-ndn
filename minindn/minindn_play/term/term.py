import os
import logging
import msgpack
import fcntl
import struct
import termios
import random
import shutil

from contextlib import redirect_stdout, redirect_stderr
from code import InteractiveConsole

from mininet.net import Mininet
from mininet.cli import CLI
from minindn.util import is_valid_hostid, host_home, getPopen
from minindn.minindn_play.consts import WSKeys, WSFunctions
from minindn.minindn_play.socket import PlaySocket
from minindn.minindn_play.term.pty_manager import Pty, PtyManager

class TermExecutor:
    pty_list: dict[str, Pty] = {}
    pty_manager: PtyManager

    def __init__(self, net: Mininet, socket: PlaySocket):
        self.net = net
        self.socket = socket
        self.pty_manager = PtyManager(self)

    def start_cli(self):
        """UI Function: Start CLI"""
        # Send logs to UI
        class WsCliHandler():
            def __init__(self, parent: TermExecutor):
                self.parent = parent

            def write(self, msg: str):
                if "cli" not in self.parent.pty_list:
                    return
                mb = msg.encode("utf-8")
                self.parent.send_pty_out(mb, "cli")
                self.parent.pty_list["cli"].buffer.write(mb)

        lg = logging.getLogger("mininet")
        handler = logging.StreamHandler(WsCliHandler(self))
        handler.terminator = ""
        lg.addHandler(handler)

        # Create pty for cli
        cpty = Pty(self, "cli", "Mininet CLI")
        self.pty_manager.register(cpty)

        # Start cli
        CLI.use_rawinput = False
        CLI(self.net, stdin=os.fdopen(cpty.slave, "r"), stdout=os.fdopen(cpty.slave, "w"))

    def start_repl(self):
        """UI Function: Start REPL"""

        cpty = Pty(self, "repl", "Python REPL")
        self.pty_manager.register(cpty)

        try:
            with os.fdopen(cpty.slave, "w") as fout, os.fdopen(cpty.slave, "r") as fin, redirect_stdout(fout), redirect_stderr(fout):
                def raw_input(prompt="") -> str:
                    print(prompt, end="", flush=True)
                    return fin.readline()
                repl = InteractiveConsole({
                    "net": self.net,
                })
                repl.raw_input = raw_input
                repl.interact(None, None)
        except OSError:
            pass

    async def open_all_ptys(self):
        """UI Function: Open all ptys currently active"""
        for key in self.pty_list:
            cpty = self.pty_list[key]
            self.socket.send_all(msgpack.dumps({
                WSKeys.MSG_KEY_FUN: WSFunctions.OPEN_TERMINAL,
                WSKeys.MSG_KEY_RESULT: self._open_term_response(cpty)
            }))

    async def open_term(self, nodeId: str):
        """UI Function: Open new bash terminal"""
        if not is_valid_hostid(self.net, nodeId):
            return

        # Get directory of node
        node_home = host_home(self.net[nodeId])

        # Copy .bashrc to node
        if node_home is not None:
            path = os.path.expanduser("~/.bashrc")
            if os.path.isfile(path):
                # Do this copy every time to make sure the file is up to date
                target = node_home + "/.bashrc"
                shutil.copy(path, target)

                # Append extra commands
                with open(target, "a") as f:
                    # Shell prompt
                    f.write("\nexport PS1='\\[\\033[01;32m\\]\\u@{}\\[\\033[00m\\]:\\[\\033[01;34m\\]\\w\\[\\033[00m\\]\\$ '\n".format(nodeId))

        # Create pty
        pty_id = nodeId + str(int(random.random() * 100000))
        pty_name = f"bash [{nodeId}]"
        cpty = Pty(self, pty_id, pty_name)
        self.pty_manager.register(cpty)

        # Start bash
        cpty.process = getPopen(self.net[nodeId], "bash --noprofile -i", stdin=cpty.slave, stdout=cpty.slave, stderr=cpty.slave)

        return self._open_term_response(cpty)

    async def pty_in(self, pty_id: str, msg: msgpack.ExtType):
        """UI Function: Send input to pty"""
        if pty_id not in self.pty_list:
            return

        if pty_id == "cli" and msg.data == b"\x03":
            # interrupt
            for node in self.net.hosts:
                if node.waiting:
                    node.sendInt()

        self.pty_list[pty_id].stdin.write(msg.data)
        self.pty_list[pty_id].stdin.flush()

    async def pty_resize(self, pty_id, rows, cols):
        """UI Function: Resize pty"""
        if pty_id not in self.pty_list:
            return

        winsize = struct.pack("HHHH", rows, cols, 0, 0)
        fcntl.ioctl(self.pty_list[pty_id].master, termios.TIOCSWINSZ, winsize)

    def send_pty_out(self, msg: bytes, pty_id: str):
        """Send output to UI"""
        self.socket.send_all(msgpack.dumps({
            WSKeys.MSG_KEY_FUN: WSFunctions.PTY_OUT,
            WSKeys.MSG_KEY_ID: pty_id,
            WSKeys.MSG_KEY_RESULT: msg,
        }))

    def _open_term_response(self, cpty: Pty):
        """Return response for open terminal"""
        return { "id": cpty.id, "name": cpty.name, "buf": cpty.buffer.read() }
