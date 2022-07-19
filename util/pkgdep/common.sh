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

# needed by Python version detection logic in Mininet install script
export PYTHON=python3

# DEP_INFO key should match *_VERSION variable name.
# DEP_INFO entry should have these comma separated fields:
# [0] local directory name
# [1] dep name
# [2] PPA package name
# [3] GitHub repository (HTTPS)
# [4] Gerrit repository (repo name only)
declare -A DEP_INFO
DEP_INFO=(
  ["CXX"]="ndn-cxx,ndn-cxx,libndn-cxx-dev,https://github.com/named-data/ndn-cxx.git,ndn-cxx"
  ["NFD"]="NFD,NFD,nfd,https://github.com/named-data/NFD.git,NFD"
  ["PSYNC"]="PSync,PSync,libpsync-dev,https://github.com/named-data/PSync.git,PSync"
  ["NLSR"]="NLSR,NLSR,nlsr,https://github.com/named-data/NLSR.git,NLSR"
  ["TOOLS"]="ndn-tools,NDN Essential Tools,ndn-tools,https://github.com/named-data/ndn-tools.git,ndn-tools"
  ["TRAFFIC"]="ndn-traffic-generator,NDN Traffic Generator,ndn-traffic-generator,https://github.com/named-data/ndn-traffic-generator.git,ndn-traffic-generator"
  ["INFOEDIT"]="infoedit,infoedit,,https://github.com/NDN-Routing/infoedit.git,"
  ["MININET"]="mininet,Mininet,,https://github.com/mininet/mininet.git,"
  ["MNWIFI"]="mininet-wifi,Mininet-WiFi,,https://github.com/intrig-unicamp/mininet-wifi.git,"
)

# command to detect dependency existence
# if not specified, dependency is assumed to not exist
declare -A DEP_DETECT
DEP_DETECT=(
  ["CXX"]="pkg-config libndn-cxx"
  ["NFD"]="command -v nfd"
  ["PSYNC"]="pkg-config PSync"
  ["NLSR"]="command -v nlsr"
  ["TOOLS"]="command -v ndnping && command -v ndncatchunks"
  ["TRAFFIC"]="command -v ndn-traffic-client"
  ["INFOEDIT"]="command -v infoedit"
  ["MININET"]="command -v mn && command -v ofdatapath && $PYTHON -m pip show mininet"
  ["MNWIFI"]="$PYTHON -m pip show mininet-wifi"
)

# non-Waf build & install command
build_INFOEDIT() {
  make -j${NJOBS}
  $SUDO make install
}
build_MININET() {
  ./util/install.sh -s ${CODEROOT} -nv
  if ! command -v ofdatapath >/dev/null; then
    rm -rf ${CODEROOT}/openflow
    ./util/install.sh -s ${CODEROOT} -f
  fi

  $SUDO $PYTHON setup.py develop
  $SUDO cp /usr/local/bin/mn /usr/local/bin/mn.mininet
}
build_MNWIFI() {
  # issue: git repository is not owned by root, causing "unsafe repository" error
  # workaround: chown the git repository to root
  $SUDO chown -R 0:0 .

  # issue: util/install.sh attempts to patch hostap every time, causing "Assume -R?" prompt
  # during reinstalls
  # workaround: revert hostap submodule to clean state
  $SUDO git -C hostap clean -fdx || true
  $SUDO git -C hostap checkout -- . || true

  # issue: util/install.sh is not setting noninteractive mode for apt-get
  # workaround: temporarily disable needrestart
  if [[ -d /etc/needrestart/conf.d ]]; then
    $SUDO tee /etc/needrestart/conf.d/99-disabled-by-minindn.conf > /dev/null <<'EOT'
$nrconf{restart} = 'l';
$nrconf{kernelhints} = 0;
EOT
  fi

  # issue: util/install.sh is not using 'sudo' where needed such as 'make install'
  # workaround: run whole script in 'sudo'
  $SUDO env PYTHON=$PYTHON ./util/install.sh -Wl

  # issue: setup.py reports "Cannot load backend 'TkAgg' which requires the 'tk' interactive
  # framework, as 'headless' is currently running" when running over SSH
  # workaround: pretend to have X11 display
  $SUDO env DISPLAY=:0 $PYTHON setup.py develop
  $SUDO cp /usr/local/bin/mn /usr/local/bin/mn.wifi

  # make 'mn' command refer to Mininet's version, which does not require X11
  if [[ -x /usr/local/bin/mn.mininet ]]; then
    $SUDO cp /usr/local/bin/mn.mininet /usr/local/bin/mn
  fi

  # chown the git repository to current user, so that user can modify code without root
  if [[ $(id -u) -ne 0 ]]; then
    $SUDO chown -R $(id -u):$(id -g) .
  fi

  # re-enable needrestart
  $SUDO rm -f /etc/needrestart/conf.d/99-disabled-by-minindn.conf
}

# Waf configure options
declare -A DEP_WAFOPTS
DEP_WAFOPTS=(
  ["NFD"]="--without-websocket"
  ["PSYNC"]="--with-examples"
)

# return whether dep is installed
dep_exists() {
  if [[ $IGNORE_EXISTING -eq 1 ]]; then
    return 2
  fi
  local DETECT="${DEP_DETECT[$1]}"
  if [[ -n $DETECT ]] && bash -c "$DETECT" &>/dev/null; then
    return 0
  fi
  return 1
}

# set to 1 if dep needs downloading
declare -A NEED_DL

# display prompt on what to do with dep, populate NEED_DL
dep_prompt() {
  local INFO=()
  IFS=',' read -a INFO <<< "${DEP_INFO[$1]}"
  local VERSION_VAR="$1_VERSION"
  local VERSION="${!VERSION_VAR}"
  if [[ -z $VERSION ]]; then
    VERSION='(default branch)'
  fi
  local DLDIR="${CODEROOT}/${INFO[0]}"
  if dep_exists $1; then
    echo "Will use existing ${INFO[1]}"
  elif [[ $PREFER_FROM == ppa ]] && [[ -n ${INFO[2]} ]]; then
    echo "Will install ${INFO[1]} from named-data PPA"
    PPA_PKGS+=("${INFO[2]}")
  elif [[ -d "$DLDIR" ]]; then
    if [[ $DL_ONLY -ne 1 ]]; then
      echo "Will install ${INFO[1]} from local checkout ${DLDIR}"
    fi
  else
    NEED_DL[$1]=1
    if [[ $DL_ONLY -eq 1 ]]; then
      echo "Will checkout ${INFO[1]} ${VERSION} to ${DLDIR}"
    else
      echo "Will download and install ${INFO[1]} ${VERSION}"
    fi
  fi
}

# download dep source code
dep_checkout() {
  if [[ ${NEED_DL[$1]} -ne 1 ]]; then
    return
  fi
  local INFO=()
  IFS=',' read -a INFO <<< "${DEP_INFO[$1]}"
  local VERSION_VAR="$1_VERSION"
  local VERSION="${!VERSION_VAR}"
  local DLDIR="${CODEROOT}/${INFO[0]}"

  if [[ -n ${INFO[4]} ]] && [[ "$VERSION" =~ ^[0-9]+,[0-9]+$ ]]; then
    local REPO="https://gerrit.named-data.net/${INFO[4]}"
    local GERRIT_CHANGE=${VERSION%,*}
    local GERRIT_PATCHSET=${VERSION#*,}
    echo "Downloading ${INFO[2]} from Gerrit (patchset ${GERRIT_CHANGE},${GERRIT_PATCHSET})"
    git clone "$REPO" "$DLDIR"
    git -C "$DLDIR" fetch origin "refs/changes/${GERRIT_CHANGE:(-2)}/${GERRIT_CHANGE}/${GERRIT_PATCHSET}"
    git -C "$DLDIR" -c advice.detachedHead=false checkout FETCH_HEAD
  elif [[ -z $VERSION ]]; then
    echo "Downloading ${INFO[1]} from GitHub (default branch)"
    git clone "${INFO[3]}" "$DLDIR"
  elif [[ "$VERSION" =~ @ ]]; then
    local REPO=${VERSION%@*}
    local BRANCH=${VERSION#*@}
    echo "Downloading ${INFO[1]} from ${REPO} (branch ${BRANCH})"
    git clone "$REPO" "$DLDIR"
    git -C "$DLDIR" -c advice.detachedHead=false checkout "$BRANCH"
  else
    echo "Downloading ${INFO[1]} from GitHub (branch ${VERSION})"
    git clone "${INFO[3]}" "$DLDIR"
    git -C "$DLDIR" -c advice.detachedHead=false checkout "$VERSION"
  fi
  git submodule update --init --recursive --progress
}

# install dep from source code
dep_install() {
  local INFO=()
  IFS=',' read -a INFO <<< "${DEP_INFO[$1]}"
  local DLDIR="${CODEROOT}/${INFO[0]}"
  if dep_exists $1 || ! [[ -d "$DLDIR" ]]; then
    return
  fi
  pushd "$DLDIR"

  local FN="build_$1"
  if declare -F $FN >/dev/null; then
    echo "Installing ${INFO[1]} with custom command"
    $FN
  elif [[ -x waf ]]; then
    echo "Installing ${INFO[1]} with Waf"
    $PYTHON ./waf configure ${DEP_WAFOPTS[$1]}
    $PYTHON ./waf -j${NJOBS}
    $SUDO $PYTHON ./waf install
  fi
  popd
}

if [[ $PPA_AVAIL -ne 1 ]] || [[ $NO_PPA -eq 1 ]]; then
  PREFER_FROM=source
fi

# dep install order, excluding ndn-cxx
DEPLIST=(NFD PSYNC NLSR TOOLS TRAFFIC INFOEDIT MININET)
if [[ $NO_WIFI -ne 1 ]]; then
  DEPLIST+=(MNWIFI)
fi

echo "Will download to ${CODEROOT}"
echo 'Will install compiler and build tools'
dep_prompt CXX
if [[ $CXX_DUMMY_KEYCHAIN -eq 1 ]]; then
  echo 'Will patch ndn-cxx to use dummy KeyChain'
fi
for DEP in "${DEPLIST[@]}"; do
  dep_prompt $DEP
done
if [[ $DL_ONLY -ne 1 ]]; then
  echo "Will compile with ${NJOBS} parallel jobs"
  echo "Will install Mini-NDN package"
fi

if [[ $CONFIRM -ne 1 ]]; then
  read -p 'Press ENTER to continue or CTRL+C to abort '
fi

install_pkgs

if [[ -z $SKIPPYTHONCHECK ]]; then
  PYTHON_VERSION=$($PYTHON --version)
  SUDO_PYTHON_VERSION=$($SUDO $PYTHON --version)
  if [[ "$PYTHON_VERSION" != "$SUDO_PYTHON_VERSION" ]]; then
    cat <<EOT
In your system, '${PYTHON}' is ${PYTHON_VERSION} and '$SUDO ${PYTHON}' is ${SUDO_PYTHON_VERSION}
You must manually resolve the conflict, e.g. delete excess Python installation or change $PATH
To bypass this check, set the environment variable SKIPPYTHONCHECK=1
EOT
    exit 1
  fi
fi

if ! mkdir -p "${CODEROOT}" 2>/dev/null; then
  $SUDO mkdir -p "${CODEROOT}"
  $SUDO chown $(id -u) "${CODEROOT}"
fi
dep_checkout CXX
if [[ $CXX_DUMMY_KEYCHAIN -eq 1 ]]; then
  echo 'Patching ndn-cxx to use dummy KeyChain'
  if ! git -C "${CODEROOT}/ndn-cxx" apply --index < "${PKGDEPDIR}/../patches/ndn-cxx-dummy-keychain.patch"; then
    echo 'Cannot patch ndn-cxx to use dummy KeyChain (possibly already patched)'
  fi
fi
for DEP in "${DEPLIST[@]}"; do
  dep_checkout $DEP
done

if [[ $DL_ONLY -eq 1 ]]; then
  cat <<EOT
Source code has been downloaded to ${CODEROOT}
You may make changes or checkout different versions
Run this script again without --dl-only to install from local checkout
EOT
  exit 0
fi

prepare_ld
for DEP in CXX "${DEPLIST[@]}"; do
  dep_install $DEP
done
$SUDO ldconfig

DESTDIR=/usr/local/etc/mini-ndn
$SUDO install -d -m0755 "$DESTDIR"
find topologies/ -name '*.conf' | xargs $SUDO install -m0644 -t "$DESTDIR/"
$SUDO $PYTHON setup.py develop

echo 'MiniNDN installation completed successfully'
