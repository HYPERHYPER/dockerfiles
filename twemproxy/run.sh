#!/bin/bash

# auto-update twemproxy config:
python /usr/src/nutcracker_aws_autoconf.py /usr/src/nutcracker.yml /etc/nutcracker.yml

# run twemproxy
nutcracker -c /etc/nutcracker.yml
