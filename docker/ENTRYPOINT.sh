#!/usr/bin/env bash

# set python3 alias, but needs permanent fix in image directly
alias python=python3

service openvswitch-switch start
ovs-vsctl set-manager ptcp:6640

bash

service openvswitch-switch stop
