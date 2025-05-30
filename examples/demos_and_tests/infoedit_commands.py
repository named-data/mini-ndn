# -*- Mode:python; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2025, The University of Memphis,
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

from mininet.log import setLogLevel, info

from minindn.minindn import Minindn
from minindn.util import MiniNDNCLI
from minindn.apps.app_manager import AppManager
from minindn.apps.nfd import Nfd
from minindn.apps.nlsr import Nlsr

if __name__ == '__main__':
    setLogLevel('info')

    Minindn.cleanUp()
    Minindn.verifyDependencies()

    ndn = Minindn()

    ndn.start()

    info('Starting NFD on nodes\n')
    # These two are synonymous; set the key to this specific value
    nfds = AppManager(ndn, ndn.net.hosts, Nfd, infoeditChanges=[["tables.strategy_choice./hello_world",
                                                                 "/localhost/nfd/strategy/asf/v=5/probing-interval~1000"],
                                                                ["tables.strategy_choice./hello_world_again",
                                                                 "/localhost/nfd/strategy/asf/v=5/probing-interval~1000", "section"],])
    info('Starting NLSR on nodes\n')
    # Put should be used when there is a non-unique key
    # Delete doesn't take a second argument but will delete the specified key and its value
    nlsrs = AppManager(ndn, ndn.net.hosts, Nlsr,  infoeditChanges=[["advertising.prefix", "/hello_world", "put"],
                                                                   ["hyperbolic.radius", "", "delete"]])

    MiniNDNCLI(ndn.net)

    ndn.stop()
