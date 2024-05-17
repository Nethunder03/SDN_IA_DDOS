#!/bin/bash

iterations=100  # Nombre d'itérations souhaitées
cd /home/mininet/Downloads/
while true; do
    for ((i = 0; i < $iterations; i++)); do
        echo "*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*"
        echo "*    $((i + 1))    *          Itération num : $((i + 1))        *   $((i + 1))         *"
        echo "*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*"

        # Boucle pour exécuter wget 20 fois
        for ((j = 1; j < 26; j++)); do
            ping -c 10 172.24.16.$j
        done

         sleep 10  # Pause de 10 secondes
        done
    done

   
done



