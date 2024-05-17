
#!/bin/bash

iterations=100  # Nombre d'itérations souhaitées
cd /home/mininet/Downloads/
while true; do
    for ((i = 0; i < $iterations; i++)); do
        echo "*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*"
        echo "*    $((i + 1))    *          Itération num : $((i + 1))        *   $((i + 1))         *"
        echo "*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*"

        # Boucle pour exécuter wget 20 fois
        for ((j = 1; j < 21; j++)); do
            #iperf -p 5051 -u -c 172.24.16.23 -b 10M
            iperf -p 5051 -u -c 172.24.16.20 -b 10M
            iperf -p 5050 -c 172.24.16.20 -b 10M
            iperf -p 5051 -u -c 172.24.16.21 -b 10M
            iperf -p 5050 -c 172.24.16.21 -b 10M
            iperf -p 5051 -u -c 172.24.16.22 -b 10M
            iperf -p 5050 -c 172.24.16.22 -b 10M
            iperf -p 5051 -u -c 172.24.16.23 -b 10M
            iperf -p 5050 -c 172.24.16.23 -b 10M
        done


    done
done

