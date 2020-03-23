Install
=======

Prerequisites
-------------

For this guide, you will need a laptop/desktop with a recent version of
a Linux distro that is supported by Mininet. For this guide, the *Ubuntu 18.04 LTS* release was used.
Some tweaks maybe required to Mini-NDN's install.sh file for other distros.
Note that you'll need administrative privileges in order to download and install
extra packages and also to execute **Mini-NDN**.

Using Vagrantfile
-----------------

With Vagrant installed, simply do ``vagrant up`` which will bring up an Ubuntu 18.04 virtual machine
and install Mini-NDN and all its dependencies on it. Please make sure to tweak the CPU core count
(default 4 cores) and RAM (default 4GB) according to your needs before doing vagrant up. Mini-NDN
can be found in /home/vagrant/mini-ndn which is a symlink to /vagrant if Vagrantfile was used from within mini-ndn cloned on the host. Otherwise it is an actual clone of mini-ndn.

Using install.sh
----------------

Mini-NDN depends on Mininet and NDN software to be installed in the system.
If you have all the dependencies (see sections below) **installed in the system** simply
clone this repository and run:

::

    ./install.sh -i

The ``-i`` option uses ``setup.py develop`` to point the system install
to the current directory. So any changes made to the cloned ``mini-ndn``
folder will be used without having to install it again to the system.
If you do not need to modify the core of Mini-NDN, then setup.py install (or pip install .)
can be used directly. See :doc:`experiment <experiment>` for more information on running.

If you don't have the dependencies, the following command will
install them from source along with Mini-NDN. The dependencies include
Mininet, NDN core (ndn-cxx, NFD, Chronosync, PSync, NLSR), Infoedit,
and NDN Common Client Libraries (CCL). If you do not wish to install
the master versions of the NDN core or want to switch to specific versions,
you can edit the install.sh with release tags/specific versions.

.. _scaling-note:
.. important::
    If you wish to scale Mini-NDN experiments and do not have use for security extensions
    in your emulations, you should apply the ndn-cxx patch given in the ``patches`` folder
    using ``./install.sh -p`` before running the following commands. The ndn-cxx patch is
    taken from ndnSIM which provides an in-memory dummy KeyChain to reduce CPU computations.
    After these patches are applied sleep time after NFD, nfdc, NLSR, etc. is not required
    making the startup **MUCH** faster and scaling of Mini-NDN **MUCH** better.

::

    ./install.sh -a

This pulls the NDN software from Github to ``ndn-src`` folder under the project.

.. note::
    If any changes are made to ``ndn-src`` folder, please don't forgot to re-install
    the sources to the system.

To install without CCL, use:

::

    ./install.sh -mni

To install in "quiet" mode (without user interaction), use:

::
    ./install.sh -qa

.. note::
    The order of the flag -q is important to ensure that the environment is ready for
    a quiet install.

See ``install.sh -h`` for detailed options.

Installing Dependencies
-----------------------

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
