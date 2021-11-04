# -*- Mode:bash; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
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

# APT packages, written in alphabetical order.
APT_PKGS=(
  build-essential
  ca-certificates
  git
  libboost-atomic-dev
  libboost-chrono-dev
  libboost-date-time-dev
  libboost-filesystem-dev
  libboost-iostreams-dev
  libboost-log-dev
  libboost-program-options-dev
  libboost-regex-dev
  libboost-stacktrace-dev
  libboost-system-dev
  libboost-thread-dev
  libpcap-dev
  libsqlite3-dev
  libssl-dev
  libsystemd-dev
  pkg-config
  python-is-python3
  python3-pip
  software-properties-common
  tshark
)

if [[ $NO_WIFI -ne 1 ]]; then
  APT_PKGS+=(network-manager)
fi

install_pkgs() {
  $SUDO apt-get update
  $SUDO env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "${APT_PKGS[@]}"
  if [[ $PPA_AVAIL -eq 1 ]] && [[ ${#PPA_PKGS[@]} -gt 0 ]]; then
    $SUDO add-apt-repository -y -u ppa:named-data/ppa
    $SUDO env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "${PPA_PKGS[@]}"
  fi
}

prepare_ld() {
  return
}
