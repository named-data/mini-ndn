# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2019, The University of Memphis,
#                          Arizona Board of Regents,
#                          Regents of the University of California.
#
# This file is part of Mini-NDN.
# See AUTHORS.md for a complete list of Mini-NDN authors and contributors.
#
# Mini-NDN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mini-NDN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mini-NDN, e.g., in COPYING.md file.
# If not, see <http://www.gnu.org/licenses/>.

import time
import sys

from mininet.log import setLogLevel, info
from mininet.topo import Topo

from minindn.minindn import Minindn
from minindn.apps.app_manager import AppManager
from minindn.apps.nfd import Nfd

if __name__ == '__main__':
    setLogLevel('info')

    topo = Topo()
    topo.addHost('h1')

    ndn = Minindn(topo=topo)
    args = ndn.args

    ndn.start()

    nfds = AppManager(ndn, ndn.net.hosts, Nfd)

    host1 = ndn.net.hosts[0]
    host1.cmd('export NDN_LOG=examples.PartialSyncProducerApp=INFO')
    host1.cmd('psync-producer /sync /{} 10 1 &> producer.log &'.format(host1.name))
    time.sleep(1)

    host1.cmd('export NDN_LOG=examples.PartialSyncConsumerApp=INFO:$NDN_LOG')
    host1.cmd('psync-consumer /sync 5 &> consumer.log &')

    info('Sleeping 90 seconds for convergence\n')
    time.sleep(90)

    consumerSubs = int(host1.cmd('cat consumer.log | grep -c Subscribing'))
    consumerUpdates = int(host1.cmd('cat consumer.log | grep -c Update'))
    producerPublish = int(host1.cmd('cat producer.log | grep -c Publish'))

    if consumerSubs == 5 and consumerUpdates == 5 and producerPublish == 10:
        info('PSync partial sync has successfully converged.\n')
    else:
        info('PSync partial sync convergence was not successful. Exiting...\n')
        ndn.stop()
        sys.exit(1)
