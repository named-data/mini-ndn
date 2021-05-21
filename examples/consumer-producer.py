# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2021, The University of Memphis,
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

from time import sleep

from mininet.log import setLogLevel, info
from minindn.minindn import Minindn
from minindn.util import MiniNDNCLI
from minindn.apps.app_manager import AppManager
from minindn.apps.nfd import Nfd
from minindn.apps.nlsr import Nlsr


"""
This example demonstrates a basic consumer-producer using Mini-NDN. It uses ndnpeek and ndnpoke as
a consumer and a producer respectively. If you want to build your own consumer/producer program, you
can take help from here: https://github.com/named-data/ndn-cxx/tree/master/examples and
here: https://github.com/dulalsaurab/multicast-supression-ndn/tree/main/ndn-src/consumer-producer
"""

if __name__ == '__main__':
    setLogLevel('info')

    Minindn.cleanUp()
    Minindn.verifyDependencies()
    ndn = Minindn()
    ndn.start()

    info('Starting nfd and nlsr on nodes')
    nfds = AppManager(ndn, ndn.net.hosts, Nfd)
    nlsrs = AppManager(ndn, ndn.net.hosts, Nlsr)
    sleep(90)

    # Default topology is used in this experiment "/topologies/default-topology.conf"
    # lets make node "a" as a producer node, and node "c" as a consumer node
    producer = ndn.net['a']
    consumer = ndn.net['c']

    # start producer
    producerPrefix = "/example"
    producer.cmd('nlsrc advertise {}'.format(producerPrefix))
    sleep(5) # sleep for routing convergence

    # Make sure that basic consumer/producer example are compiled and installed in the system
    info('Starting consumer and producer application')
    producer.cmd("echo 'HELLO WORLD' | ndnpoke {} &> producer.log &".format(producerPrefix))
    consumer.cmd("ndnpeek -p {} &> consumer.log &".format(producerPrefix))

    MiniNDNCLI(ndn.net)
    ndn.stop()