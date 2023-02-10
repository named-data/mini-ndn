# Mini-NDN

Mini-NDN is a lightweight networking emulation tool that enables testing, experimentation, and
research on the NDN platform based on [Mininet](https://github.com/mininet/mininet).
Mini-NDN uses the NDN libraries, NFD, NLSR, and tools released by the
[NDN project](http://named-data.net/codebase/platform/) to emulate an NDN network on a single system.

Mini-NDN works on Ubuntu 20.04 and 22.04. It will also run on Debian 11 and Fedora 33 without the WiFi scenario.

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

## Quickstart

To run Mini-NDN with the default toplology, run:

```bash
sudo python examples/mnndn.py
```

To run Mini-NDN with a topology file, provide a filname as the first argument:

```bash
sudo python examples/mnndn.py my-topology.conf
```

More information on how to make your own topologies and configuration file can be found [here](https://mini-ndn.readthedocs.io/en/latest/experiment.html#configuration)

A sample experiment can be found in [/experiments](/experiments) or in the documentaion [here](https://mini-ndn.readthedocs.io/en/latest/experiment.html#sample).

## Documentation

Full documentation for Mini-NDN can be found at its [ReadTheDocs](https://mini-ndn.readthedocs.io/en/latest/).

Alternatively, the docs can be built from source by cloning this repo and running:

```bash
./docs/build.sh
```

The output can be found in `docs/_build/html`.

Additionally, the [ICN 2022 presentation](https://named-data.net/wp-content/uploads/2022/09/3-ICN22-Mini-NDN.pdf) is a good starting point to get an overview.

## Contributing

If you are new to the NDN community of software generally, read the
[Contributor's Guide](https://github.com/named-data/.github/blob/master/CONTRIBUTING.md).

Mini-NDN is open and free software licensed under the GPL 3.0 license. Mini-NDN is free to all
users and developers. For more information about licensing details and limitations,
please refer to [COPYING.md](COPYING.md).

The first release of Mini-NDN is developed by members of the NSF-sponsored NDN project team.
Mini-NDN is open to contribution from the public.
For more details, please refer to [AUTHORS.rst](AUTHORS.rst).
Bug reports and feedback are highly appreciated and can be made through our
[Redmine site](http://redmine.named-data.net/projects/mini-ndn) and the
[mini-ndn mailing list](http://www.lists.cs.ucla.edu/mailman/listinfo/mini-ndn).

Learn more about Mini-NDN's dependencies:

- [Mininet](http://mininet.org)
- [Mininet-wifi](https://mininet-wifi.github.io) (optional)
- [NDN Forwarding Daemon (NFD)](https://docs.named-data.net/NFD/current/)
- [Named Data Link State Routing (NLSR)](https://docs.named-data.net/NLSR/current/)
- [NDN Essential Tools (ndn-tools)](https://github.com/named-data/ndn-tools)
- [NDN Traffic Generator](https://github.com/named-data/ndn-traffic-generator)
- [ndn-cxx](https://docs.named-data.net/ndn-cxx/current/INSTALL.html)
