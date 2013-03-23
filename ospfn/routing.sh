#!/bin/bash
#sleep 1
zebra -d -f zebra.conf -i /var/run/quagga-state/zebra.$1.pid
#sleep 1
ospfd -f ospfd.conf -i /var/run/quagga-state/ospfd.$1.pid -d -a
#sleep 5
#ospfn -d -f ospfn.conf

