# -*- Mode:bash; c-file-style:"gnu"; indent-tabs-mode:nil -*- */
#
# Copyright (C) 2015-2022, The University of Memphis,
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

if [[ $VERSION_ID -lt 33 ]]; then
  cat <<EOT
Fedora 33 or newer is required
Installation on older versions may fail
EOT
fi

# DNF packages, written in alphabetical order.
DNF_PKGS=(
  boost-devel
  ca-certificates
  gcc-c++
  libpcap-devel
  openssl-devel
  python3-pip
  sqlite-devel
  systemd-devel
)

install_pkgs() {
  $SUDO dnf install -y "${DNF_PKGS[@]}"
}

prepare_ld() {
  if ! $SUDO ldconfig -v 2>/dev/null | grep -q /usr/local/lib64; then
    echo 'Enabling /usr/local/lib64 in dynamic linker'
    $SUDO mkdir -p /etc/ld.so.conf.d
    echo /usr/local/lib64 | $SUDO tee /etc/ld.so.conf.d/usr-local-lib64.conf >/dev/null
  fi
}

# ndn-cxx installs to /usr/local/lib64, but `pkg-config --libs libndn-cxx` by default strips out
# `-L/usr/local/lib64` flag. This environ or `pkg-config --keep-system-libs` prevents that.
export PKG_CONFIG_ALLOW_SYSTEM_LIBS=1
