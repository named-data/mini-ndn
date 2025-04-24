import fcntl, struct, termios, os
import subprocess
import select
import pty
from io import BufferedWriter
from threading import Thread
from typing import TYPE_CHECKING

import msgpack

from minindn.minindn_play.term.cbuf import CircularByteBuffer
from minindn.minindn_play.consts import WSKeys, WSFunctions

if TYPE_CHECKING:
    from minindn.minindn_play.term.term import TermExecutor


class Pty:
    id: str
    name: str
    master: int
    slave: int
    stdin: BufferedWriter
    buffer: CircularByteBuffer
    executor: 'TermExecutor'
    process: subprocess.Popen | None = None

    def __init__(self, executor, pty_id: str, name: str):
        """
        Initialize a new pty
        Creates a new Python PTY instance and stores the slave and master file descriptors
        """
        self.master, self.slave = pty.openpty()
        self.buffer = CircularByteBuffer(16000)
        self.executor = executor
        self.id = pty_id
        self.name = name
        self.stdin = os.fdopen(self.master, 'wb')
        executor.pty_list[self.id] = self

    def cleanup(self):
        """Cleanup the pty"""

        self.executor.socket.send_all(msgpack.dumps({
            WSKeys.MSG_KEY_FUN: WSFunctions.CLOSE_TERMINAL,
            WSKeys.MSG_KEY_ID: self.id,
        }))

        try:
            os.close(self.master)
            os.close(self.slave)
        except OSError:
            pass

        if self.id in self.executor.pty_list:
            del self.executor.pty_list[self.id]

class PtyManager:
    ptys = {}
    thread: Thread
    executor: 'TermExecutor'
    poller = select.poll()

    def __init__(self, executor):
        """Initialize the pty manager"""
        self.executor = executor
        self.thread = Thread(target=self._ui_thread, args=(), daemon=True)
        self.thread.start()

    def register(self, target_pty: Pty):
        """Register a new pty with the manager"""
        self.ptys[target_pty.master] = target_pty
        self.poller.register(target_pty.master, select.POLLIN)

    def unregister(self, target_pty: Pty):
        """Unregister a pty from the manager"""
        self.poller.unregister(target_pty.master)
        target_pty.cleanup()
        if target_pty.master in self.ptys:
            del self.ptys[target_pty.master]

    def _ui_thread(self):
        """Thread that handles UI output"""
        while True:
            self._check_procs()
            self._poll_fds()

    def _check_procs(self):
        """Check if any processes have exited and unregister them"""
        for target_pty in list(self.ptys.values()):
            if target_pty.process is not None and target_pty.process.poll() is not None:
                self.unregister(target_pty)
                continue

    def _poll_fds(self):
        """Poll all registered file descriptors"""
        for (fd, status) in self.poller.poll(250):
            if fd not in self.ptys:
                self.poller.unregister(fd)
                continue
            target_pty = self.ptys[fd]

            # Check if poller is closed
            if status == select.POLLHUP:
                self.unregister(target_pty)
                continue

            # Find the number of bytes available to read
            bytes_available = fcntl.ioctl(target_pty.master, termios.FIONREAD, struct.pack('I', 0))
            bytes_available = struct.unpack('I', bytes_available)[0]
            bytes_to_read = min(bytes_available, 4096)

            # This should never really happen
            if bytes_to_read == 0:
                continue

            # Read everything available and send to UI
            try:
                out_bytes = os.read(target_pty.master, bytes_to_read)
                self.executor.send_pty_out(out_bytes, target_pty.id)
                target_pty.buffer.write(out_bytes)
            except Exception as e:
                print(e)
                self.unregister(target_pty)
                continue
