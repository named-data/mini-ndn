import time

from mininet.log import setLogLevel, info

from minindn.wifi.minindnwifi import MinindnWifi
from minindn.apps.app_manager import AppManager
from minindn.apps.nfd import Nfd
from minindn.apps.nlsr import Nlsr
from minindn.helpers.experiment import Experiment

setLogLevel('info')

# Setup code
sync = Nlsr.SYNC_PSYNC

ndn = MinindnWifi()
args = ndn.args

ndn.start()

info('Starting NFD on nodes\n')
nfds = AppManager(ndn, ndn.net.stations, Nfd, logLevel='INFO')
face_dict = ndn.setupFaces()

if not face_dict:
    print("Hint: Are you sure you're running with a topology with a faces section? \
           Try topologies/wifi/nlsr_wifi_example.conf")

info('Starting NLSR on nodes\n')
nlsrs = AppManager(ndn, [], Nlsr)

print(face_dict)

for host in ndn.net.stations:
    nlsrs.startOnNode(host, sync=sync, logLevel='INFO', faceDict=face_dict)
    time.sleep(0.1)

Experiment.checkConvergence(ndn, ndn.net.stations, 60, False)

# Uncomment for CLI access
from minindn.util import MiniNDNWifiCLI
MiniNDNWifiCLI(ndn.net)

ndn.stop()