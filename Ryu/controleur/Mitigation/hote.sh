#!/bin/bash

iterations=100  # Nombre d'itérations
cd /home/mininet/Downloads/
while true; do
    for ((i = 0; i < $iterations; i++)); do
        echo "*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*"
        echo "*    $((i + 1))    *          Itération num : $((i + 1))        *   $((i + 1))         *"
        echo "*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*"

        # Boucle pour exécuter wget 20 fois
        for ((j = 1; j < 21; j++)); do
            wget http://172.24.16.20/index.html
            wget http://172.24.16.21/index.html
            wget http://172.24.16.22/index.html
            wget http://172.24.16.23/index.html
            wget http://172.24.16.20/test.zip
            wget http://172.24.16.21/test.zip
            wget http://172.24.16.22/test.zip
            wget http://172.24.16.23/test.zip
            iperf -p 5051 -u -c 172.24.16.20
            iperf -p 5050 -c 172.24.16.20
            iperf -p 5051 -u -c 172.24.16.21
            iperf -p 5050 -c 172.24.16.21
            iperf -p 5051 -u -c 172.24.16.22
            iperf -p 5050 -c 172.24.16.22
            iperf -p 5051 -u -c 172.24.16.23
            iperf -p 5050 -c 172.24.16.23
        done

        # Supprimer des fichiers dans /home/mininet/Downloads
        rm -f /home/mininet/Downloads/*
        done
        
        sleep 10  # Pause de 10 secondes
    done

done
