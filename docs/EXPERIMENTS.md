Experiments
===========

Mini-NDN includes an experimentation framework which allows a user to create and automate
networking experiments. Users can run existing experiments, included with Mini-NDN, or define
their own custom experiment.

## Running existing experiments

Mini-NDN includes three example experiments that can be used to test the network or as reference
for custom experiment implementations. `ndn-tools` must be installed to run the example
experiments as each experiment uses both `ndnpingserver` and `ndnping`. Please see
[INSTALL.md](../INSTALL.md) for instructions on installing `ndn-tools`.

To see a list of the available experiments, run Mini-NDN using the `--list-experiments` parameter:

    minindn --list-experiments

To run an experiment, provide the experiment name as an argument to the `--experiment` parameter:

    sudo minindn --experiment=pingall

Each experiment will run until completion or exit if there is an error setting up the
test environment.

The three included experiments are set up using the same starting
configuration. Each node runs NFD, NLSR, and an ndnpingserver which advertises the node's
site name. After a waiting period to allow the network to converge (default is 60 seconds),
the convergence status of the network is checked. If each node's FIB does not have an entry
for every other node's router name and advertised prefix, the experiment is aborted and an error
is reported.

#### Common experiment parameters

The time allowed for convergence (in seconds) can be configured using the `--ctime` parameter:

    sudo minindn --ctime=30 ...

After the experiment has finished running, the command-line interface (CLI) will be launched and the
user can then interact with the test environment. To disable the CLI and instead exit Mini-NDN
as soon as the experiment has finished, use the `--no-cli` parameter:

    sudo minindn --no-cli ...

To ping only a percentage of nodes `--pct-traffic` can be set.

    sudo minindn --pct-traffic=0.5 ...

The above command will ping only 50% of other nodes from each node.
The default value is 1 i.e. ping every other node.

To move the experiment results to a results directory from the working directory
after the experiment is complete (either --no-cli or quit) the following option
can be used:

    sudo minindn --result-dir /home/mydir/result-dir ...

The included experiments are described in detail below along with additional
parameters that can be provided to modify the execution of the experiments.

### Pingall experiment

**Scenario**: Each node in the network simultaneously pings every other node in the network at a
one second interval.

**Experiment ID**: `--pingall`

The number of pings sent in the experiment can be configured using the `--nPings` parameter:

    sudo minindn --experiment=pingall --nPings=120

By default, `--nPings` is 300 for the Pingall experiment.

### Failure experiment

**Scenario**: Each node in the network simultaneously pings every other node in the network at a
one second interval. After 60 seconds, the node with the name "csu" is brought down. The node is
left in a failed state for 120 seconds while the other nodes continue pinging. After this period,
the failed node is recovered and pings are collected for an additional 90 seconds.

**Experiment ID**: `--failure`

`--nPings` is 300 for the Failure experiment and cannot be modified.

### Multiple failure experiment

**Scenario**: Each node in the network simultaneously pings every other node in the network at a
one second interval. After 60 seconds, the first node in the network will be brought down and remain
in failed state for 60 seconds. After the failure period, the node is recovered and the network
is allowed to recover for 60 seconds. After the recovery period, the next node will go through this
failure and recovery process. Once every node in the network has gone through the failure and
recovery process, the experiment will end.

**Experiment ID**: `--multiple-failure`

`--nPings` is dependent on the size of the topology being tested. 120 pings are scheduled for
each node's failure/recovery period as well as an additional 60 pings for the initial collection
period.

### MCN failure experiment

**Scenario**: This is exactly like the failure experiment but instead of failing the node named "csu" it fails the most connected node (MCN) i.e the node with the most links.

Experiment ID: `--mcn-failure`

### Experiment data

The ping data is stored at `/tmp/minindn/node-name/ping-data`.

The ping server log is stored at `/tmp/minindn/node-name/ping-server`

## Creating custom experiments

Mini-NDN provides a simple Python based framework which allows a user to define their own experiment
and run it from the command line.

To create an experiment, follow these steps:

1. Create a Python source file for the experiment in the `ndn/experiments` directory.

   e.g.) `ndn/experiments/example.py`

2. Derive the experiment from the `Experiment` base class defined in
   `ndn/experiments/experiment.py`.

        #!/usr/bin/python

        from ndn.experiments.experiment import Experiment

        class ExampleExperiment(Experiment):
            def __init__(self, args):
                Experiment.__init__(self, args)

3. Override `start()` if the experiments want to override NLSR setup and skip `setup()` and `run()`
as described below. `start()` is the entry point for an experiment.

4. Override the `setup()` method to define how the experiment should be initialized

   e.g.) Run an ndnping server in the background on each node

        def setup(self):
           for host in self.net.hosts:
               host.cmd("ndnpingserver host.name &")


5. Override the `run()` method to define how the experiment should behave

    e.g.) Obtain the NFD status of each node and save it to file

        def run(self):
            for host in self.net.hosts:
                host.cmd("nfdc status report > status.txt")

6. Register the experiment with the `ExperimentManager` to make the experiment runnable from the
command line.

        Experiment.register("example-name", ExampleExperiment)

The experiment can then be run from the command-line using the name registered.
"example-name" in the above example:

        sudo minindn --experiment=example-name

### Full example experiment code

    #!/usr/bin/python

    from ndn.experiments.experiment import Experiment

    class ExampleExperiment(Experiment):
        def __init__(self, args):
            Experiment.__init__(self, args)

        def setup(self):
            for host in self.net.hosts:
                host.cmd("ndnpingserver host.name &")

        def run(self):
            for host in self.net.hosts:
                # By default status.txt would be stored
                # at /tmp/minindn/host/status.txt
                host.cmd("nfdc status report > status.txt")

    Experiment.register("example-name", ExampleExperiment)

## Passing arguments to experiments

Mini-NDN has the capacity to pass arguments to experiments, insofar
as they do not clash with those of Mini-NDN. This feature
allows users to pass arguments to Mini-NDN and process them in an
experiment without having to rewrite Mini-NDN's core.

An example of an experiment implementing this functionality is given in
`ndn/experiments/arguments_experiment.py`, which demonstrates how to
write code which handles arguments. Documentation for these arguments
appears when called with `sudo minindn -h`, as does documentation for
fixed arguments defined in core code, so it is strongly recommended to
differentiate those you write yourself. Note that Bash and Zsh users
can make use of autocomplete functionality when calling these arguments.

To run the experiment:

    sudo minindn --experiment arg-exp --ds 226 --logging

The experiment will print out the supplied value for --ds and a boolean
value for the presence of --logging. --experiment is a fixed argument of
Mini-NDN.