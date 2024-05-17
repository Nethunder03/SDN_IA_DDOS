#!/bin/bash

cd /home/mininet/serveurweb

python3 -m http.server 80 &
python3 -m http.server 443 &
iperf -s -p 5050 &
iperf -s -u -p 5051 &

