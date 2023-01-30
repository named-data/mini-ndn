# Mini-NDN

If you are new to the NDN community of software generally, read the
[Contributor's Guide](https://github.com/named-data/.github/blob/master/CONTRIBUTING.md).

## What is Mini-NDN?

Mini-NDN is a lightweight networking emulation tool that enables testing, experimentation, and
research on the NDN platform based on [Mininet](https://github.com/mininet/mininet).
Mini-NDN uses the NDN libraries, NFD, NLSR, and tools released by the
[NDN project](http://named-data.net/codebase/platform/) to emulate an NDN network on a single system.

Mini-NDN is open and free software licensed under the GPL 3.0 license. Mini-NDN is free to all
users and developers. For more information about licensing details and limitations,
please refer to [COPYING.md](COPYING.md).

The first release of Mini-NDN is developed by members of the NSF-sponsored NDN project team.
Mini-NDN is open to contribution from the public.
For more details, please refer to [AUTHORS.rst](AUTHORS.rst).
Bug reports and feedback are highly appreciated and can be made through our
[Redmine site](http://redmine.named-data.net/projects/mini-ndn) and the
[mini-ndn mailing list](http://www.lists.cs.ucla.edu/mailman/listinfo/mini-ndn).

Mini-NDN works on Ubuntu 20.04. It will also run on Debian 11 and Fedora 33 without the WiFi scenario.

Mini-NDN's dependencies are:

- Mininet
- Mininet-wifi (optional)
- NDN Forwarding Daemon (NFD)
- Named Data Link State Routing (NLSR)
- NDN Essential Tools (ndn-tools)
- NDN Traffic Generator
- ndn-cxx
- Infoedit

## Installation

Mini-NDN can be installed from source using the following commands:

```bash
git clone https://github.com/named-data/mini-ndn.git
cd mini-ndn
./install.sh --source
```

`./install.sh --source` will install NDN packages from source.

`./install.sh --ppa` will install NDN packages from PPA repository.

`./install.sh --[source or ppa] --no-wifi` will install Mini-NDN without the wifi module.

## Documentation

Please refer to [this presentation](https://named-data.net/wp-content/uploads/2022/09/3-ICN22-Mini-NDN.pdf) from ICN 2022 or [docs/index.rst](docs/index.rst) for installation, usage, and other documentation.
The documentation can be built using:

```bash
./docs/build.sh
```

and is available under `docs/_build/html`.
