#!/bin/bash
killall -r ccnd ospf zebra
rm log*
rm */*log
rm -rf /var/run/quagga-state/*
