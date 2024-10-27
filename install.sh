#!/bin/bash
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

set -eo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

# These commands are generally installed on most systems. If not, user must install manually.
# 'sudo' is not directly used by this script, but Mininet install.sh uses it, so we check that also.
NEEDED_BINARIES=(
  awk
  git
  sudo
)
MISSING_BINARIES=()

SUDO=
if [[ $(id -u) -eq 0 ]]; then
  if [[ -n $SUDO_USER ]] && [[ -z $SKIPSUDOCHECK ]]; then
    cat <<EOT
Do not run this script through sudo
Instead, run this script as a regular user; the script will call sudo when needed
To bypass this check, set the environment variable SKIPSUDOCHECK=1
EOT
    exit 1
  fi
else
  SUDO=sudo
fi

for B in "${NEEDED_BINARIES[@]}"; do
  if ! command -v "$B" >/dev/null; then
    MISSING_BINARIES+=("$B")
  fi
done
if [[ ${#MISSING_BINARIES[@]} -gt 0 ]] ; then
  echo "Missing commands (${MISSING_BINARIES[*]}) to start this script. To install, run:"
  echo "  $SUDO apt install --no-install-recommends ca-certificates curl git mawk sudo"
  echo "  $SUDO yum install ca-certificates curl git mawk sudo"
  exit 1
fi

CODEROOT="$(pwd)/dl"
NJOBS=$(nproc)
MEM_JOBS=$(awk '$1=="MemAvailable:" { print int($2/(1536*1024)); exit }' /proc/meminfo)
if [[ $MEM_JOBS -lt 1 ]]; then
  NJOBS=1
  echo 'Insufficient available RAM, build may fail'
elif [[ $MEM_JOBS -lt $NJOBS ]]; then
  NJOBS=$MEM_JOBS
fi
PREFER_FROM=ppa
PPA_PKGS=()

ARGS=$(getopt -o 'hy' -l 'help,dir:,jobs:,no-wifi,ppa,source,release:,cxx:,dummy-keychain,nfd:,psync:,nlsr:,tools:,traffic:,infoedit:,mininet:,mnwifi:,dl-only,use-existing' -- "$@")
eval set -- "$ARGS"
while true; do
  case $1 in
    -h|--help) HELP=1; shift;;
    -y) CONFIRM=1; shift;;
    --dir) CODEROOT=$2; shift 2;;
    --jobs) NJOBS=$((0+$2)); shift 2;;
    --no-wifi) NO_WIFI=1; shift;;
    --ppa) PREFER_FROM=ppa; shift;;
    --source) PREFER_FROM=source; shift;;
    --release) RELEASE_VERSION=$2; source util/releases/current_release.sh; NO_PPA=1; shift 2;;
    --cxx) CXX_VERSION=$2; NO_PPA=1; shift 2;;
    --dummy-keychain) CXX_DUMMY_KEYCHAIN=1; NO_PPA=1; shift;;
    --nfd) NFD_VERSION=$2; NO_PPA=1; shift 2;;
    --psync) PSYNC_VERSION=$2; NO_PPA=1; shift 2;;
    --nlsr) NLSR_VERSION=$2; NO_PPA=1; shift 2;;
    --tools) TOOLS_VERSION=$2; NO_PPA=1; shift 2;;
    --traffic) TRAFFIC_VERSION=$2; NO_PPA=1; shift 2;;
    --infoedit) INFOEDIT_VERSION=$2; shift 2;;
    --mininet) MININET_VERSION=$2; shift 2;;
    --mnwifi) MNWIFI_VERSION=$2; shift 2;;
    --dl-only) DL_ONLY=1; shift;;
    --use-existing) USE_EXISTING=1; shift;;
    --) shift; break;;
    *) exit 1;;
  esac
done

if [[ $NJOBS -le 0 ]]; then
  cat <<EOT
--jobs must be a positive integer.
Run ./install.sh -h to see help message.
EOT
  exit 1
fi

if [[ $HELP -eq 1 ]]; then
  cat <<EOT
./install.sh [OPTION]...

General options:
  -h  Display help and exit.
  -y  Skip confirmation.
  --dir=${CODEROOT}
      Set where to download and compile the code.
  --jobs=${NJOBS}
      Set number of parallel jobs.
  --no-wifi
      Do not install Mininet-WiFi.

Install preference options:
  --ppa
      Install available packages from named-data PPA.
      This is the default on Ubuntu, unless a source code version option is used.
  --source
      Install all packages from source code.

Source code version options:
  --release=[RELEASE]
      Use specified major release. To install the most recent, use 'current'. A list of
      other possible values is located in the installation docs.
  --cxx=[VERSION]
      Set ndn-cxx version.
  --dummy-keychain
      Patch ndn-cxx to use dummy KeyChain.
      This disables signing and verifications, which allows experiments to run faster.
      Use this option only if your scenario does not require signature verification.
  --nfd=[VERSION]
      Set NFD version.
  --psync=[VERSION]
      Set PSync version.
  --nlsr=[VERSION]
      Set NLSR version.
  --tools=[VERSION]
      Set NDN Essential Tools version.
  --traffic=[VERSION]
      Set NDN Traffic Generator version.
  --infoedit=[VERSION]
      Set infoedit version.
  --mininet=[VERSION]
      Set Mininet version.
  --mnwifi=[VERSION]
      Set Mininet-WiFi version.
Acceptable version syntaxes:
  * git commit/tag/branch, example: --nfd=NFD-0.7.1
  * git repository (e.g. fork) and commit/tag/branch, example:
      --nfd=https://github.com/named-data/NFD.git@NFD-0.7.1
  * change,patchset on named-data Gerrit, example: --nfd=6236,8

Misc options:
  --dl-only
      Download the source code only.
      You may modify the code in ${CODEROOT} and then rerun this script to install them.
  --use-existing
      Use already installed dependency binaries and libraries, rather than attempting to
      reinstall. This is useful if you have modified source code checkout for some
      repositories but still want to install any remaining dependencies or are
      reinstalling Mini-NDN.
EOT
  exit 0
fi

trap 'set +e; trap - ERR; echo "Error!"; exit 1;' ERR

PKGDEPDIR="$(pwd)/util/pkgdep"
if [[ -e /etc/os-release ]]; then
  source /etc/os-release
fi
for id in ${ID,,} ${ID_LIKE,,}; do
  if [[ -e $PKGDEPDIR/$id.sh ]]; then
    source "$PKGDEPDIR/$id.sh"
    source "$PKGDEPDIR/common.sh"
    exit 0
  fi
done
echo "Unsupported platform ${ID}, aborting"
exit 1
