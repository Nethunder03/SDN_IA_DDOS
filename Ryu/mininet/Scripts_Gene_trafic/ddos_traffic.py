from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.node import OVSKernelSwitch, RemoteController
from time import sleep
from datetime import datetime
from random import randrange, choice
from random import choice
import threading

class MyTopo(Topo):
    def build(self):
        hotes = []
        switchs = []
        serveurs = []

        # Ajout de 18 hôtes
        for i in range(1, 19):
            mac = ":".join([f"{randrange(256):02x}" for _ in range(6)])
            hote = self.addHost(f'h{i}', cpu=1.0/20, mac=mac, ip=f'172.24.16.{i}/24')
            hotes.append(hote)

        # Ajout de 15 commutateurs
        for i in range(1, 16):
            switch = self.addSwitch(f's{i}', cls=OVSKernelSwitch, protocols='OpenFlow13')
            switchs.append(switch)

        # Ajout de 4 serveurs
        for i in range(1, 5):
            serveur = self.addHost(f'serv{i}', mac=f'02:00:00:00:00:0{i}', ip=f'172.24.16.{i + 19}/24')
            serveurs.append(serveur)

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

        # Liaisons entre commutateurs
        self.addLink(switchs[0], switchs[1])
        self.addLink(switchs[0], switchs[2])
        self.addLink(switchs[0], switchs[3])
        self.addLink(switchs[0], switchs[13])

        self.addLink(switchs[1], switchs[4])
        self.addLink(switchs[1], switchs[5])
        self.addLink(switchs[1], switchs[6])

        self.addLink(switchs[3], switchs[7])
        self.addLink(switchs[3], switchs[8])
        self.addLink(switchs[3], switchs[9])

        self.addLink(switchs[2], switchs[10])
        self.addLink(switchs[2], switchs[11])
        self.addLink(switchs[2], switchs[12])

        self.addLink(switchs[14], switchs[3])

        self.addLink(switchs[14], serveurs[0])
        self.addLink(switchs[14], serveurs[1])
        self.addLink(switchs[14], serveurs[2])
        self.addLink(switchs[14], serveurs[3])

def start_servers_and_iperf(net):
    for i in range(1, 5):
        serveur = net.get(f'serv{i}')
        serveur.cmd(f'cd /home/mininet/serveurweb && python -m http.server 80 &')
        serveur.cmd(f'cd /home/mininet/serveurweb && python -m http.server 443 &')
        serveur.cmd('iperf -s -p 5050 &')
        serveur.cmd('iperf -s -u -p 5051 &')
        sleep(2)

def generate_traffic(src, dst):
    dst_ip = dst.IP()  # Obtenez l'adresse IP de l'hôte de destination
    attack_types = ["ICMP", "UDP", "TCP-SYN", "SMURF", "HTTP"]
    num_attackers = 5  # Nombre d'attaquants simultanés

    for i in range(600):
        for _ in range(num_attackers):
            attack = choice(attack_types)
            print(f"*=*=" * 15 + "*\n"
                    f"              Exécution d'une inondation {attack}               \n" +
                    f"*=*=" * 15 +"*")
            if attack == "TCP-SYN":
                src.cmd(f'timeout 20s hping3 -S -V -d 120 -w 64 -p 80 --rand-source --flood 172.24.16.20')
                src.cmd(f'timeout 20s hping3 -S -V -d 120 -w 64 -p 80 --rand-source --flood 172.24.16.21')
            elif attack == "SMURF":
                src.cmd(f'timeout 20s hping3 -1 -V -d 120 -w 64 -p 80 --rand-source --flood -a {dst_ip} {dst_ip}')
            elif attack == "HTTP":
                src.cmd(f'timeout 20s hping3 -S -V -d 120 -w 64 -p 80 -c 10000 --rand-source --flood 172.24.16.20')
                src.cmd(f'timeout 20s hping3 -S -V -d 120 -w 64 -p 8080 -c 10000 --rand-source --flood 172.24.16.22')
            else:
                proto = 1 if attack == "ICMP" else 2
                src.cmd(f'timeout 20s hping3 -{proto} -V -d 120 -w 64 -p 80 -c 10000 --rand-source --flood {dst_ip}')


def ip_generator():
    ip = ".".join(["172","24","16",str(randrange(1, 19))])
    return ip

def startNetwork():
    topo = MyTopo()
    c0 = RemoteController('c0', ip='192.168.1.14', port=6653)
    net = Mininet(topo=topo, link=TCLink, controller=c0)

    net.start()
    hote_rec = []
    start_servers_and_iperf(net)

    for i in range(1, 19):
        nom_hote = f'h{i}'
        objet_hote = net.get(nom_hote)
        hote_rec.append(objet_hote)

    for h in hote_rec:
        h.cmd('cd /home/mininet/Downloads')

    for i in range(600):
        threads = []
        for src in hote_rec:
            dst = choice(hote_rec)
            while src == dst:
                dst = choice(hote_rec)
            thread = threading.Thread(target=generate_traffic, args=(src, dst))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()


    print(f"*=*=" * 15 + "*")

    net.stop()

if __name__ == '__main__':
    start_time = datetime.now()
    setLogLevel('info')
    startNetwork()
    end_time = datetime.now()
    print(end_time - start_time)
