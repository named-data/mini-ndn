Topologies
==========

The format for topology files is not that complicated. A minimal topology file would look like this:

    [stations]
    
    [accessPoints]
    
    [links]
    
Of course, this topology would not be very useful. A more useful, familiar example would be:

    [stations]
    a: _
    b: _
    
    [accessPoints]
    ap: _
    
    [links]
    a:ap
    b:ap
    
This would create a very simple topology, with two nodes, connected via a single access point.

More detailed documentation about writing topology files can be found in the Mini-NDN repository, [here](https://github.com/named-data/mini-ndn/blob/master/docs/CONFIG.md).
