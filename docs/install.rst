Install
=======

Prerequisites
-------------

Mini-NDN is tested on the following Linux distributions:

- Ubuntu 20.04 (recommended)
- Ubuntu 22.04
- Debian 11 (WiFi scenario does not work)
- Fedora 33 (WiFi scenario does not work)

You must have sudo privileges to install and run Mini-NDN.

Using Vagrantfile
-----------------

With Vagrant installed, simply do ``vagrant up`` which will bring up an Ubuntu 18.04 virtual machine
and install Mini-NDN and all its dependencies on it. Please make sure to tweak the CPU core count
(default 4 cores) and RAM (default 4GB) according to your needs before doing vagrant up. Mini-NDN
can be found in /home/vagrant/mini-ndn which is a symlink to /vagrant if Vagrantfile was used from within mini-ndn cloned on the host. Otherwise it is an actual clone of mini-ndn.

Using install.sh
----------------

Mini-NDN has the following dependencies:

- `NDN Forwarding Daemon (NFD) <https://named-data.net/doc/NFD/>`_
- `Named Data Link State Routing (NLSR) <https://named-data.net/doc/NLSR/>`_
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

IMPORTANT: For now, Mininet-WiFi only works with ``--source`` installation because the current NFD release (0.7.1) doesn't
incorporate `issue 5155 <https://redmine.named-data.net/issues/5155>`, a required patch for WiFi module to work properly.
With the next NFD release, Mininet-WiFi will work with both ``source`` and ``ppa``. Alternatively, you can
checkout (at your own risk) a third-party source "`Use NFD nightly with Mini-NDN <https://yoursunny.com/t/2021/NFD-nightly-minindn/>`", which provides
NFD-nightly version and contains all the necessary patches. 

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

This section outlines how to install dependnecies manually.
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

Mini-NDN uses NFD, NLSR, and ndn-tools.

- To install NFD: https://named-data.net/doc/NFD/current/INSTALL.html
- To install NLSR: https://named-data.net/doc/NLSR/current/INSTALL.html
- To install ndn-tools: https://github.com/named-data/ndn-tools

.. warning::
    Please do not try to install NDN software from both the source (GitHub) and PPA (apt).
    It will not work in most cases! If you used ./install.sh -a in the past but now want
    to use apt, please run ``sudo ./waf uninstall`` in all the NDN projects before proceeding
    with apt. Similarly, remove from apt if switching to source.

Please see the :ref:`scaling-note <scaling-note>` to learn about disabling
security for better scalability.

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
