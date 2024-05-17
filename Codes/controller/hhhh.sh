#!/bin/bash

iterations=100  # Nombre d'itérations souhaitées
cd /home/mininet/Downloads/
while true; do
    for ((i = 0; i < $iterations; i++)); do
        echo "*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*"
        echo "*    $((i + 1))    *          Itération num : $((i + 1))        *   $((i + 1))         *"
        echo "*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*"
        
        # Fonction pour générer une adresse IP avec Python
        generate_ip() {
            python3 - <<'END'
import random

def ip_generator():
    ip = ".".join(["172", "24", "16", str(random.randint(1, 19))])
    return ip

print(ip_generator())
END
        }

        # Boucle pour exécuter wget 20 fois
        for ((j = 1; j < 21; j++)); do
            dst_ip=$(generate_ip)
            iperf -p 5051 -u -c "$dst_ip" -b 10M
        done
    done
done

