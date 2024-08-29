# -*- Mode:bash; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2024, The University of Memphis,
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

RELEASE_FILE="util/releases/$RELEASE_VERSION.sh"


if [[ $RELEASE_VERSION == current ]]; then
    # THIS SHOULD BE UPDATED ON MAJOR RELEASES
    RELEASE_FILE="util/releases/2024-08.sh"
fi

if [[ ! -e $RELEASE_FILE ]]; then
    cat <<EOT
No valid release version passed as argument. Please check
documentation and your command for typos.

Valid versions:
 - current
 - 2024-08

Exiting...
EOT
    exit 1
fi

source "$RELEASE_FILE"

# This prevents issues when manually overriden versions
# are specified before the release by checking if these
# vars are already set.

: ${CXX_VERSION:=${CXX_RELEASE}}
: ${NFD_VERSION:=${NFD_RELEASE}}
: ${PSYNC_VERSION:=${PSYNC_RELEASE}}
: ${NLSR_VERSION:=${NLSR_RELEASE}}
: ${TOOLS_VERSION:=${TOOLS_RELEASE}}
: ${TRAFFIC_VERSION:=${TRAFFIC_RELEASE}}
: ${INFOEDIT_VERSION:=${INFOEDIT_RELEASE}}