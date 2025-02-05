Install
=======

Prerequisites
-------------

Mini-NDN is officially supported on the following Linux distributions:

- Ubuntu 20.04
- Ubuntu 22.04 (recommended)
- Ubuntu 24.04
- Debian 11 (WiFi scenario does not work)
- Fedora 33 (WiFi scenario does not work)

You must have sudo privileges to install and run Mini-NDN.

Using Docker
------------

You can use the nightly build from GitHub package registry
::
    docker run -m 4g --cpus=4 -it --privileged \
            -v /lib/modules:/lib/modules \
            ghcr.io/named-data/mini-ndn:master bash

NOTE: This nightly build is only currently supported for x86_64. ARM64 support
(i.e. Apple silicon Macs) will be added in the future.

Building your own Docker image
------------------------------

The provided Dockerfile can be used to build an image from scratch. To build with the Dockerfile:
  - Clone the repository and type::

        docker build -t minindn .

  - You can then access the container through shell with::

        docker run -m 4g --cpus=4 -it --privileged \
            -v /lib/modules:/lib/modules \
            minindn bin/bash

Additional recommendations
--------------------------
- It is recommended to set reasonable constraints on memory (`-m`) and CPU cores (`--cpus`), especially on less
  powerful or non-dedicated systems.
- `--privileged` is mandatory for underlying `Mininet <http://mininet.org/>`_ to utilize the virtual switch
- The root directory on `run` is `/mini-ndn`, which contains the installation and examples.
- The GUI may not work for now due to docker and xterm setup issues and is independent from Mini-NDN.
  If you intend to run the GUI, pass `-e DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix` to the `docker run` command.

Using Vagrantfile
-----------------

With Vagrant installed, simply do ``vagrant up`` which will bring up an Ubuntu 18.04 virtual machine
and install Mini-NDN and all its dependencies on it. Please make sure to tweak the CPU core count
(default 4 cores) and RAM (default 4GB) according to your needs before doing vagrant up. Mini-NDN
can be found in /home/vagrant/mini-ndn which is a symlink to /vagrant if Vagrantfile was used from within mini-ndn cloned on the host. Otherwise it is an actual clone of mini-ndn.

Using install.sh
----------------

Mini-NDN has the following dependencies:

- `NDN Forwarding Daemon (NFD) <https://docs.named-data.net/NFD/current/>`_
- `Named Data Link State Routing (NLSR) <https://docs.named-data.net/NLSR/current/>`_
- `NDN Essential Tools (ndn-tools) <https://github.com/named-data/ndn-tools>`_
- `NDN Traffic Generator <https://github.com/named-data/ndn-traffic-generator>`_
- `infoedit <https://github.com/NDN-Routing/infoedit>`_
- `Mininet <http://mininet.org/>`_
- `Mininet-WiFi <https://mininet-wifi.github.io/>`_ (optional)

To install Mini-NDN and its dependencies, clone this repository and run:

::

    ./install.sh

The script accepts various command line flags.
Some notable flags are:

- ``-y`` skips interactive confirmation before installation.
- ``--ppa`` prefers installing NDN software from `named-data PPA <https://launchpad.net/~named-data/+archive/ubuntu/ppa>`_.
  This shortens installation time by downloading binary packages, but is only available on Ubuntu.
- ``--source`` prefers installing NDN software from source code.
- ``--use-existing`` will only install dependencies not already in the executable path.
- ``--dummy-keychain`` patches ndn-cxx to use an in-memory dummy KeyChain, which reduces CPU overhead
  and allows you to scale up Mini-NDN experiments. Large Mini-NDN experiments would run significantly
  faster after applying this patch. However, your experiments cannot use any NDN security related
  features (signatures, verifier, access control, etc).
- ``--no-wifi`` skips Mininet-WiFi dependency.
  Currently Mininet-WiFi only works on Ubuntu, so that you must specify this option when installing on other distros.

You can see all command line flags by running:

::

    ./install.sh -h

The script uses ``setup.py develop`` to point the system install of Python packages to the codebase
directory. Therefore, you can modify ``mininet``, ``mininet-wifi``, and ``mini-ndn``, and the
changes will be reflected immediately.

If NDN software is installed from source code (not PPA), the code is downloaded to ``dl`` directory
under your ``mini-ndn`` clone. If you modify the source code, you need to manually recompile and
reinstall the software (``./waf && sudo ./waf install``).


Installing Dependencies
-----------------------

This section outlines how to install dependencies manually.
If you used ``install.sh``, you do not need to perform these steps.

Mininet
_______

Mini-NDN is based on Mininet. To install Mininet:

::

    git clone --depth 1 https://github.com/mininet/mininet.git

After Mininet source is on your system, run the following command to
install Mininet core dependencies and Open vSwitch:

::

    ./util/install.sh -nv

To check if Mininet is working correctly, run this test:

::

    sudo mn --test pingall

This will print out a series of statements that show the test setup and
the results of the test. Look for ``Results:`` two-thirds of the way
down where it will indicate the percentage of dropped packets. Your
results should show "0% dropped (2/2 received)".

NOTE: Mini-NDN, while providing a high level of emulation of hosts,
requires programs to be installed onto your computer. It will not work
if they are not installed. If you do not want NDN software installed
onto your computer, you can use a virtual machine, which can be quite
simply set up with the provided Vagrantfile.

NDN dependencies
________________

Each node in Mini-NDN will run the official implementation of NDN
installed on your system. The following dependencies are needed:

Mini-NDN uses ndn-cxx, NFD, NLSR, and ndn-tools.

- To install ndn-cxx: https://docs.named-data.net/ndn-cxx/current/INSTALL.html
- To install NFD: https://docs.named-data.net/NFD/current/INSTALL.html
- To install NLSR: https://docs.named-data.net/NLSR/current/INSTALL.html
- To install ndn-tools: https://github.com/named-data/ndn-tools/blob/master/INSTALL.md

.. warning::
    Please do not try to install NDN software from both the source (GitHub) and PPA (apt).
    It will not work in most cases! If you used ./install.sh -a in the past but now want
    to use apt, please run ``sudo ./waf uninstall`` in all the NDN projects before proceeding
    with apt. Similarly, remove from apt if switching to source.

In cases where using NDN security is not important to the results, it is recommended
to use the dummy keychain patch for ndn-cxx to disable it for improved scalability.
This patch is located at `util/patches/ndn-cxx-dummy-keychain.patch.`

Note that all three of these can be installed from the Named Data PPA.
Instructions for setting it up can be found in the NFD installation
instructions. Note that PPA and installs from source **cannot** be
mixed. You must completely remove PPA installs from the system if switching
to source and vice-versa.

For PPA installs, if you are using a custom nfd.conf file in an experiment, you should
place it in /usr/local/etc/ndn/ rather than /etc/ndn/. This is to avoid
a bug from the default configuration file for the PPA, which is
incompatible with Mini-NDN.

Infoedit
________

Infoedit is used to edit configuration files for NFD and NLSR.
To install infoedit:

::

    git clone --depth 1 https://github.com/NDN-Routing/infoedit
    cd infoedit
    make
    sudo make install

Verification
------------

You can execute the following example to bring up the Mini-NDN command line
with NFD and NLSR running on each node:

::

    sudo python examples/mnndn.py

You can use these steps to run the sample pingall experiment:

1. Issue the command: ``sudo python examples/nlsr/pingall.py``
2. When the ``mini-ndn>`` CLI prompt appears, the experiment has
   finished. On the Mini-NDN CLI, issue the command ``exit`` to exit the
   experiment.
3. Issue the command:
   ``grep -c content /tmp/minindn/*/ping-data/*.txt``. Each file should
   report a count of 50.
4. Issue the command:
   ``grep -c timeout /tmp/minindn/*/ping-data/*.txt``. Each file should
   report a count of 0.


Release Versions
----------------

We provide a set of shortcuts to install major release versions of NDN
dependencies from source.

You can install the most recent release using:

::

    ./install.sh --source --release=current

You can also select a specified release using:

::

    ./install.sh --source --release=[chosen version]


Currently, the compatible versions include:

- ``2024-08``: ndn-cxx 0.9.0, NFD 24.07, NLSR 24.08, PSync 0.5.0,
  ndn-tools 24.07, and compatible versions of ndn-traffic-generator
  and infoedit.

Using gpsd (Experimental)
----------------

The gpsd application included currently is based on in-progress work and
is not treated as part of the main dependencies. To use it, install the
`gpsd` and `nc` (netcat) from your package manager, if not already present,
to enable the functionality.