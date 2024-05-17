from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.node import OVSKernelSwitch, RemoteController
from time import sleep
from datetime import datetime
from random import randrange, choice
import random

class MyTopo(Topo):
    def build(self):
        hotes = []
        switchs = []

        for i in range(1, 19):
            mac = ":".join([f"{random.randint(0, 255):02x}" for _ in range(6)])
            hote = self.addHost(f'h{i}', cpu=1.0/20, mac=mac, ip=f'172.24.16.{i}/24')
            hotes.append(hote)


        for i in range(1, 14):
            switch= self.addSwitch(f's{i}', cls=OVSKernelSwitch, protocols='OpenFlow13')
            switchs.append(switch)

 
       # Liaisons entre hôtes et commutateurs
        #Rack 1
        self.addLink(hotes[0], switchs[4])
        self.addLink(hotes[1], switchs[4])
        self.addLink(hotes[2], switchs[5])
        self.addLink(hotes[3], switchs[5])

        

        #Rack 2
        self.addLink(hotes[4], switchs[6])
        self.addLink(hotes[5], switchs[6])
        self.addLink(hotes[6], switchs[7])
        self.addLink(hotes[7], switchs[7])


        #Rach 3
        self.addLink(hotes[8], switchs[8])
        self.addLink(hotes[9], switchs[8])
        self.addLink(hotes[10], switchs[9])
        self.addLink(hotes[11], switchs[9])



        self.addLink(hotes[12], switchs[10])
        self.addLink(hotes[13], switchs[10])
        self.addLink(hotes[14], switchs[11])
        self.addLink(hotes[15], switchs[11])
        self.addLink(hotes[16], switchs[12])
        self.addLink(hotes[17], switchs[12])

        # Liaisons entre les commutateurs
        self.addLink(switchs[0], switchs[1])
        self.addLink(switchs[0], switchs[2])
        self.addLink(switchs[0], switchs[3])

        self.addLink(switchs[1], switchs[4])
        self.addLink(switchs[1], switchs[5])
        self.addLink(switchs[1], switchs[6])

        self.addLink(switchs[3], switchs[7])
        self.addLink(switchs[3], switchs[8])
        self.addLink(switchs[3], switchs[9])

        self.addLink(switchs[2], switchs[10])
        self.addLink(switchs[2], switchs[11])
        self.addLink(switchs[2], switchs[12])

def ip_generator():
    ip = ".".join(["172","24","16",str(randrange(1, 19))])
    return ip

def start_network():
    topo = MyTopo()
    c0 = RemoteController('c0', ip='192.168.1.25', port=6653)
    net = Mininet(topo=topo, link=TCLink, controller=c0)
    net.start()

    hote_rec = []
    for i in range(1, 19):
        nom_hote = f'h{i}'
        objet_hote = net.get(nom_hote)
        hote_rec.append(objet_hote)


    h1 = hote_rec[0]
    h1.cmd('cd /home/mininet/serveurweb')
    h1.cmd('python3 -m http.server 80 &')

    attack_types = ["ICMP", "UDP", "TCP-SYN", "SMURF"]

    for attack in attack_types:
        src = choice(hote_rec)
        dst = ip_generator()
        print("-" * 80)
        print(f"Exécution d'une inondation {attack}")
        print("-" * 80)
        if attack == "TCP-SYN":
            src.cmd(f'timeout 20s hping3 -S -V -d 120 -w 64 -p 80 --rand-source --flood 172.24.16.1')
        elif attack == "SMURF":
            src.cmd(f'timeout 20s hping3 -1 -V -d 120 -w 64 -p 80 --rand-source --flood -a {dst} {dst}')
        else:
            proto = 1 if attack == "ICMP" else 2
            src.cmd(f'timeout 20s hping3 -{proto} -V -d 120 -w 64 -p 80 --rand-source --flood {dst}')
        sleep(100)

    net.stop()

if __name__ == '__main__':
    start_time = datetime.now()
    setLogLevel('info')
    start_network()
    end_time = datetime.now()
    print(end_time - start_time)
