# Mini-NDN

![Latest version](https://img.shields.io/github/v/tag/named-data/mini-ndn?label=Latest%20version)
[![Docker](https://github.com/named-data/mini-ndn/actions/workflows/docker.yml/badge.svg)](https://github.com/named-data/mini-ndn/actions/workflows/docker.yml)

### What is Mini-NDN?

Mini-NDN is a lightweight networking emulation tool that enables testing, experimentation, and
research on the NDN platform based on [Mininet](https://github.com/mininet/mininet).
Mini-NDN uses the NDN libraries, NFD, NLSR, and tools released by the
[NDN project](https://named-data.net/codebase/platform/) to emulate an NDN network on a single system.

Mini-NDN is free and open source software distributed under the GNU General Public License version 3.
For more information about licensing details and limitations, please refer to [`COPYING.md`](COPYING.md).

The first release of Mini-NDN is developed by members of the NSF-sponsored NDN project team.
For more details, please refer to [`AUTHORS.rst`](AUTHORS.rst).
Bug reports and feedback are highly appreciated and can be made through our
[Redmine site](https://redmine.named-data.net/projects/mini-ndn) and the
[mini-ndn mailing list](https://www.lists.cs.ucla.edu/mailman/listinfo/mini-ndn).

Mini-NDN is open to contribution from the public.
If you are new to the NDN software community and intend to contribute to the codebase, please read our
[Contributor's Guide](https://github.com/named-data/.github/blob/main/CONTRIBUTING.md).

### Documentation

Please refer to <https://minindn.memphis.edu/> for installation, usage, and other documentation.
The documentation can also be built locally using:

```shell
./docs/build.sh
```

and is available under `docs/_build/html`.
