Mini-NDN cluster edition
========================

Mini-NDN cluster edition uses the experimental Mininet cluster edition.
**Make sure that you can run the Mininet cluster edition by following
[these instructions](https://github.com/mininet/mininet/wiki/Cluster-Edition-Prototype)**.
Mini-NDN will use the "mininet" username created in Mininet cluster edition setup.

## Mini-NDN cluster options

To run Mini-NDN cluster on `localhost` and another server `server1` with
the guided node placement strategy (default), the following command can be used:

    sudo minindn --cluster=localhost,server1 --place-list=1,3

Note that `place-list` specifies the number of nodes to be placed on the corresponding servers
of the cluster.
In the example, one node will be placed on `localhost` and three nodes on `server1`.
Unless specified, the default 4 node topology is used.
Another placement can be `roundRobin` placement algorithm from Mininet.
This does not require a place-list.

    sudo minindn --cluster=localhost,server1 --placement roundRobin

By default the tunnel type used is SSH, but GRE tunnel can be specified by `--tunnel-type=gre`
