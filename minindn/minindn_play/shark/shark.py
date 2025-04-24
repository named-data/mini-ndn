import ipaddress
from pathlib import Path
from threading import Thread

import msgpack

from mininet.net import Mininet
from mininet.log import error, info
from minindn.minindn_play.socket import PlaySocket
from minindn.minindn_play.consts import Config, WSFunctions, WSKeys
from minindn.util import is_valid_hostid, run_popen, run_popen_readline

# TShark fields
SHARK_FIELDS = [
    "frame.number",
    "frame.time_epoch",
    "ndn.len",
    "ndn.type",
    "ndn.name",
    "ip.src",
    "ip.dst",
    "ipv6.src",
    "ipv6.dst",
    # "ndn.bin", # binary data
]
SHARK_FIELDS_STR = " -Tfields -e " + " -e ".join(SHARK_FIELDS) + " -Y ndn.len"

class SharkExecutor:
    _ip_map: dict = None
    _lua_script: str = None

    def __init__(self, net: Mininet, socket: PlaySocket):
        self.net = net
        self.socket = socket

    def _get_pcap_file(self, name):
        return f"./{name}-interfaces.pcap"

    def _get_lua(self):
        if self._lua_script is not None:
            return self._lua_script

        lua_path = Path(__file__).parent.parent.absolute() / "ndn.lua"
        if lua_path.exists():
            luafile = str(lua_path)
            self._lua_script = 'lua_script:' + luafile
            return self._lua_script

        luafile = '/usr/local/share/ndn-dissect-wireshark/ndn.lua'
        if Path(luafile).exists():
            self._lua_script = 'lua_script:' + luafile
            return self._lua_script

        raise RuntimeError('NDN Wireshark dissector not found (ndn-tools/ndn.lua)')

    def _convert_to_full_ip_address(self, ip_address: str):
        try:
            ip_obj = ipaddress.ip_address(ip_address)
        except ValueError:
            return ip_address

        if isinstance(ip_obj, ipaddress.IPv6Address):
            return str(ip_obj)
        else:
            return ip_address

    def _get_hostname_from_ip(self, ip):
        #TODO: This is probably overcomplicated given the Mininet API
        """
        Get the hostname of a node given its IP address.
        node: the node to check on (e.g. for local addresses)
        This function runs once and caches the result, since we need to visit
        each node to get its list of IP addresses.
        """
        if self._ip_map is None:
            # Map of IP address to hostname
            self._ip_map = {}

            # Extract all addresses including localhost
            cmd = "ip addr show | grep -E 'inet' | awk '{print $2}' | cut -d '/' -f1"

            hosts = self.net.hosts
            hosts += getattr(self.net, "stations", []) # mininet-wifi
            for host in hosts:
                for ip in host.cmd(cmd).splitlines():
                    if full_ip := self._convert_to_full_ip_address(ip):
                        self._ip_map[full_ip] = host.name
            info(f"Created IP map for PCAP (will be cached): {self._ip_map}\n")

        if full_ip := self._convert_to_full_ip_address(ip):
            return self._ip_map.get(full_ip, ip)
        return ip

    def _send_pcap_chunks(self, node_id: str, known_frame: int, include_wire: bool):
        """
        Get, process and send chunks of pcap to UI
        Blocking; should run in its own thread.
        """

        node = self.net[node_id]
        file = self._get_pcap_file(node_id)

        # We don't want to load and process the entire pcap file
        # every time the user wants to recheck. Instead, use editcap
        # to cut the part the user knows

        # Look back by upto 12 frames in case the last packet was fragmented
        known_frame = max(1, known_frame - 12)

        # Get everything after known frame
        editcap_cmd = f"editcap -r {file} /dev/stdout {known_frame}-0"

        # Shark using NDN dissector
        extra_fields = "-e ndn.bin " if include_wire else ""
        list_cmd = f"tshark {SHARK_FIELDS_STR} {extra_fields} -r /dev/stdin -X '{self._get_lua()}'"

        # Pipe editcap to tshark
        piped_cmd = ["bash", "-c", f"{editcap_cmd} | {list_cmd}"]

        # Collected packets (one chunk)
        packets = []

        def _send_packets(last=False):
            """Send the current chunk to the UI (including empty)"""
            res = {
                "id": node_id,
                "packets": packets,
            }
            if last:
                res["last"] = True

            self.socket.send_all(msgpack.dumps({
                WSKeys.MSG_KEY_FUN: WSFunctions.GET_PCAP,
                WSKeys.MSG_KEY_RESULT: res,
            }))

        # Iterate each line of output
        for line in run_popen_readline(node, piped_cmd):
            parts: list[str] = line.decode("utf-8").strip("\n").split("\t")

            if len(parts) < 8:
                error(f"Invalid line in pcap: {parts}\n")
                continue

            is_ipv6 = parts[7] != "" and parts[8] != ""
            from_ip = parts[7] if is_ipv6 else parts[5]
            to_ip = parts[8] if is_ipv6 else parts[6]

            packets.append([
                int(parts[0]) + known_frame - 1, # frame number
                float(parts[1]) * 1000, # timestamp
                int(parts[2]), # length
                str(parts[3]), # type
                str(parts[4]), # NDN name
                str(self._get_hostname_from_ip(from_ip)), # from
                str(self._get_hostname_from_ip(to_ip)), # to
                bytes.fromhex(parts[9]) if include_wire else 0, # packet content
            ])

            if len(packets) >= Config.PCAP_CHUNK_SIZE:
                _send_packets()
                packets = []

        # Send the last chunk
        _send_packets(last=True)

    async def get_pcap(self, node_id: str, known_frame: int, include_wire=False):
        """UI Function: Get list of packets for one node"""
        if not is_valid_hostid(self.net, node_id):
            return

        # Run processing in separate thread
        t = Thread(target=self._send_pcap_chunks, args=(node_id, known_frame, include_wire), daemon=True)
        t.start()

    async def get_pcap_wire(self, node_id, frame):
        """UI Function: Get wire of one packet"""
        if not is_valid_hostid(self.net, node_id):
            return
        file = self._get_pcap_file(node_id)

        # chop the file to the frame
        # include the last 12 frames in case of fragmentation
        start_frame = max(1, frame - 12)
        new_frame = frame - start_frame + 1

        try:
            # Get last 12 frames
            editcap_cmd = f"editcap -r {file} /dev/stdout {start_frame}-{frame}"

            # Filter for this packet only
            wire_cmd = f"tshark -r - -e ndn.bin -Tfields -X {self._get_lua()} frame.number == {new_frame}"

            # Pipe editcap to tshark
            piped_cmd = ["bash", "-c", f"{editcap_cmd} | {wire_cmd}"]
            hex_output = run_popen(self.net[node_id], piped_cmd).decode("utf-8").strip()
            return bytes.fromhex(hex_output)
        except Exception:
            error(f"Error getting pcap wire for {node_id}")
