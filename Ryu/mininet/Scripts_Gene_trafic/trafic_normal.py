from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.node import OVSKernelSwitch, RemoteController
from time import sleep
from datetime import datetime
from random import randrange, choice
import threading

class MyTopo(Topo):

    def build(self):
        hotes = []
        switchs = []
        serveurs = []

        # Ajout de 20 hôtes
        for i in range(1, 21):
            mac = ":".join([f"{randrange(256):02x}" for _ in range(6)])
            hote = self.addHost(f'h{i}', cpu=1.0/20, mac=mac, ip=f'172.24.16.{i}/24')
            hotes.append(hote)

        # Ajout de 20 commutateurs
        for i in range(1, 21):
            switch = self.addSwitch(f's{i}', cls=OVSKernelSwitch, protocols='OpenFlow13')
            switchs.append(switch)

        # Ajout de 4 serveurs
        for i in range(1, 5):
            serveur = self.addHost(f'serv{i}', mac=f'02:a7:00:00:00:0{i*i}', ip=f'172.24.16.{i + 20}/24')
            serveurs.append(serveur)

        # Liaisons entre hôtes et commutateurs
        for rack in range(1, 6):
            for i in range(4):
                host_index = i + (rack - 1) * 4
                switch_index = (rack - 1) * 2 + (i // 2) + 6
                #hotes.append((host_index, switch_index))
                self.addLink(hotes[host_index], switchs[switch_index])
        
        # Liaisons entre serveur et commutateurs
        for i in range(1, 3):
            self.addLink(switchs[17], serveurs[i-1])
            self.addLink(switchs[18], serveurs[i+1])


        # Liaisons entre commutateurs
        for i in range(5):
            self.addLink(switchs[0], switchs[i + 1])

        for i in range(3):
            self.addLink(switchs[1], switchs[i + 6])
            self.addLink(switchs[3], switchs[i + 9])
            self.addLink(switchs[2], switchs[i + 12])
        
        self.addLink(switchs[4], switchs[17])
        self.addLink(switchs[2], switchs[15])
        self.addLink(switchs[5], switchs[18])
        self.addLink(switchs[3], switchs[16])

def start_servers_and_iperf(net):
    for i in range(1, 5):
        serveur = net.get(f'serv{i}')
        serveur.cmd(f'cd /home/mininet/serveurweb && python -m SimpleHTTPServer 80 &')
        serveur.cmd('iperf -s -p 5050 &')
        serveur.cmd('iperf -s -u -p 5051 &')

            # Ajout de services FTP et SSH
        serveur.cmd('sudo service vsftpd start')
        serveur.cmd('sudo service ssh start')
        sleep(2)

def generate_traffic(src, dst):
    dst_ip = dst.IP()  # Obtenez l'adresse IP de l'hôte de destination
    for j in range(10):
        if j < 9:
            print("Génération du trafic ICMP entre %s et %s et du trafic TCP/UDP entre %s et les serveurs" % (src.name, dst.name, src.name))
            src.cmd(f"ping {dst_ip} -c 100 &")
            for k in range(1, 5):
                src.cmd(f"iperf -p 5050 -c 172.24.16.{k + 19}")
                src.cmd(f"iperf -p 5051 -u -c 172.24.16.{k + 19}")
        else:
            print("Génération du trafic ICMP entre %s et %s et du trafic TCP/UDP entre %s et les serveurs" % (src.name, dst.name, src.name))
            src.cmd(f"ping {dst_ip} -c 100 &")
            for k in range(1, 5):
                src.cmd(f"iperf -p 5050 -c 172.24.16.{k + 19}")
                src.cmd(f"iperf -p 5051 -u -c 172.24.16.{k + 19}")

    

def download_files(src, net):
    print(f"Téléchargement de fichiers depuis {src}")
    serveur = net.get('serv1', 'serv2', 'serv3', 'serv4')  # Sélectionnez tous les serveurs
    serveur_dst = choice(serveur)
    # Téléchargement de fichiers via HTTP
    print(f"{src} Téléchargement de index.html depuis un serveur 1")
    src.cmd(f"wget http://172.24.16.20/index.html")
    print(f"{src} Téléchargement de test.zip depuis un serveur 1")
    src.cmd(f"wget http://172.24.16.20/test.zip")
    print(f"{src} Téléchargement de index.html depuis un serveur 2")
    src.cmd("wget http://172.24.16.21/index.html")
    print(f"{src} Téléchargement de test.zip depuis un serveur 2")
    src.cmd("wget http://172.24.16.21/test.zip")
    print(f"{src} Téléchargement de index.html depuis un serveur 3")
    src.cmd("wget http://172.24.16.22/index.html")
    print(f"{src} Téléchargement de test.zip depuis un serveur 3")
    src.cmd("wget http://172.24.16.22/test.zip")
    print(f"{src} Téléchargement de index.html depuis un serveur 4")
    src.cmd("wget http://172.24.16.23/index.html")
    print(f"{src} Téléchargement de test.zip depuis un serveur 4")
    src.cmd("wget http://172.24.16.23/test.zip")

   
def ip_generator():
    ip = ".".join(["172", "24", "16", str(randrange(1, 19))])
    return ip

def startNetwork():
    topo = MyTopo()
    c0 = RemoteController('c0', ip='192.168.1.7', port=6653)
    net = Mininet(topo=topo, link=TCLink, controller=c0)

    net.start()
    hote_rec = []
    start_servers_and_iperf(net)

    for i in range(1, 21):
        nom_hote = f'h{i}'
        objet_hote = net.get(nom_hote)
        hote_rec.append(objet_hote)


    for h in hote_rec:
        h.cmd('cd /home/mininet/Downloads')

    for i in range(600):
        print(f"*=*=" * 15 + "*\n"
            f"*    {i + 1}    *          Itération num : {i + 1}        *   {i + 1}         *\n" +
            f"*=*=" * 15 +"*")
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
        for src in hote_rec:
            download_files(src, net)

        for i in range(1, 5):
            serveur = net.get(f'serv{i}')
            serveur.cmd("rm -f *.* /home/mininet/Downloads")

    print(f"*-*-" * 15 + "*")

    net.stop()

if __name__ == '__main__':
    debut = datetime.now()
    setLogLevel( 'info' )
    startNetwork()
    fin = datetime.now()
    print(fin-debut)
   
