Release Notes
=============

Mini-NDN version 0.2.0 (changes since version 0.1.1)

Release date: August 18, 2016

**New featues**:

- Automatic security configuration for NLSR

- Use /usr/local/etc/ndn/nfd.conf as default config file for NFD

- Class to monitor /proc/$PID/stat file for PID

- Mini-NDN exits gracefully on SIGINT and non-convergence

- Faster Mini-NDN install script - does not do apt-get update everytime

- NLSR is launched with explicit config file for easier process identification

- Add and update more documentation

**Bug fixes**:

- NFD is killed correctly on exit

- Best route strategy is set correctly

Mini-NDN version 0.1.1 (changes since version 0.1.0)
----------------------------------------

Release date: November 4, 2015

**New features**:

- Use nfd.conf.sample from currently installed NFD

- Add working directory option to allow execution environment outside of /tmp

- Add results directory option to store experiment results after completion

- Add support for switches in GUI and configuration file

- Add failNode and recoverNode methods to Experiment class

- Add most connected node (MCN) failure experiment

- Add option to specify percentage of nodes pinged

**Code changes**:

- Refactor program options into container class

- Remove unused "FIB Entries" option from NDN host options

**Bug fixes**:

- Abort start up if experiment name is invalid

- Restart pings after recovery in failure experiment

Mini-NDN version 0.1.0 (initial release)
----------------------------------------

Release date: July 15, 2015

Mini-NDN is a lightweight networking emulation tool that enables testing, experimentation, and
research on the NDN platform. Based on Mininet, Mini-NDN uses the NDN libraries, NFD, NLSR, and
tools released by the [NDN project](http://named-data.net/codebase/platform/) to emulate
an NDN network on a single system.

**Included features**:

- Run a complete NDN network on a single system

- Automatic configuration of NLSR to provide a routable NDN network

- Supports user created NDN applications

- Create a topology using the included Mini-NDN Edit GUI application

- Allows individual configuration of NFD and NLSR parameters for each node

- Provides an experiment management framework for easy creation of custom networking experiments

- Uses a simple topology file format to define hosts, links, and configuration values

- Configure network link parameters including bandwidth, delay, and loss rate

- Includes a pre-configured topology file to replicate the NDN testbed
