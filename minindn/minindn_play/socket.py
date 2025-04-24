import os
import asyncio
import urllib
import msgpack
import secrets
import time
import webbrowser
from threading import Thread

import websockets

from mininet.log import error
from minindn.minindn_play.consts import Config, WSKeys

class PlaySocket:
    conn_list: dict = {}
    executors: list = []
    AUTH_TOKEN: str | None = None

    def __init__(self):
        """Initialize the PlaySocket.
        This starts the background loop and creates the websocket server.
        Calls to UI async functions are made from this class.
        """
        self._set_auth_token()
        self.loop = asyncio.new_event_loop()
        Thread(target=self.loop.run_forever, args=(), daemon=True).start()
        self.loop.call_soon_threadsafe(self.loop.create_task, self._run())

    def add_executor(self, executor):
        self.executors.append(executor)

    def send(self, websocket, msg):
        """Send message to UI threadsafe"""
        if websocket.state == websockets.protocol.State.OPEN:
            self.loop.call_soon_threadsafe(self.loop.create_task, websocket.send(msg))

    def send_all(self, msg):
        """Send message to all UI threadsafe"""
        for websocket in self.conn_list.copy():
            try:
                self.send(websocket, msg)
            except Exception as err:
                error(f'Failed to send to {websocket.remote_address} with error {err}\n')
                del self.conn_list[websocket]

    def _set_auth_token(self):
        """Create auth token if it doesn't exist."""
        # Perist auth token so you don't need to refresh every time
        # Check if AUTH_FILE was modified less than a day ago
        if os.path.exists(Config.AUTH_FILE) and time.time() - os.path.getmtime(Config.AUTH_FILE) < 24 * 60 * 60:
            with open(Config.AUTH_FILE, 'r') as f:
                self.AUTH_TOKEN = f.read().strip()

        if not self.AUTH_TOKEN or len(self.AUTH_TOKEN) < 10:
            self.AUTH_TOKEN = secrets.token_hex(16)
            with open(Config.AUTH_FILE, 'w') as f:
                f.write(self.AUTH_TOKEN)

    async def _run(self) -> None:
        """Runs in separate thread from main"""
        # Show the URL to the user
        ws_url = f"ws://{Config.SERVER_HOST_URL}:{Config.SERVER_PORT}"
        ws_url_q = urllib.parse.quote(ws_url.encode('utf8'))
        full_url = f"{Config.PLAY_URL}/?minindn={ws_url_q}&auth={self.AUTH_TOKEN}"
        print(f"Opened NDN Play GUI at {full_url}")
        webbrowser.open(full_url, 1)

        # Start server
        asyncio.set_event_loop(self.loop)

        server = await websockets.serve(self._serve, Config.SERVER_HOST, Config.SERVER_PORT)
        await server.serve_forever()

    async def _serve(self, websocket):
        """Handle websocket connection"""

        try:
            path = websocket.request.path
            auth = urllib.parse.parse_qs(urllib.parse.urlparse(path).query)['auth'][0]
            if auth != self.AUTH_TOKEN:
                raise Exception("Invalid auth token")
        except Exception:
            print(f"Rejected connection from {websocket.remote_address}")
            await websocket.close()
            return

        print(f"Accepted connection from {websocket.remote_address}")
        self.conn_list[websocket] = 1
        while True:
            try:
                fcall = msgpack.loads(await websocket.recv())
                loop = asyncio.get_event_loop()
                loop.create_task(self._call_fun(websocket, fcall))
            except websockets.exceptions.ConnectionClosedOK:
                print(f"Closed connection gracefully from {websocket.remote_address}")
                break
            except websockets.exceptions.ConnectionClosedError:
                print(f"Closed connection with error from {websocket.remote_address}")
                break

        del self.conn_list[websocket]

    async def _call_fun(self, websocket, fcall):
        """Call function and return result to UI asynchronously"""

        # Get function from any executor
        fun = None
        for executor in self.executors:
            fun = getattr(executor, fcall[WSKeys.MSG_KEY_FUN], None)
            if fun is not None:
                break

        # Function not found
        if fun is None:
            error(f"Function {fcall[WSKeys.MSG_KEY_FUN]} not found\n")
            return # function not found

        # Call function
        res = await fun(*fcall[WSKeys.MSG_KEY_ARGS])
        if res is not None:
            pack = msgpack.dumps({
                WSKeys.MSG_KEY_FUN: fcall[WSKeys.MSG_KEY_FUN],
                WSKeys.MSG_KEY_RESULT: res,
            })
            await websocket.send(pack)
