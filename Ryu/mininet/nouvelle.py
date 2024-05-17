from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.node import OVSKernelSwitch, RemoteController
from random import randrange

class MonTopo(Topo):
    def build(self):
        hotes = []
        switchs = []
        #serveurs = []

        # Ajout de 20 hôtes
        for i in range(1, 27):
            mac = ":".join([f"{randrange(256):02x}" for _ in range(6)])
            hote = self.addHost(f'h{i}', cpu=1.0/20, mac=mac, ip=f'172.24.16.{i}/24')
            hotes.append(hote)

        # Ajout de 20 commutateurs
        for i in range(1, 30):
            switch = self.addSwitch(f's{i}', cls=OVSKernelSwitch, protocols='OpenFlow13')
            switchs.append(switch)
            
        '''# Ajout de 4 serveurs
        for i in range(1, 5):
            serveur = self.addHost(f'serv{i}', mac=f'02:a7:00:00:00:0{i*i}', ip=f'172.24.16.{i + 29}/24')
            serveurs.append(serveur)
        
        # Liaisons entre serveur et commutateurs
        for i in range(1, 3):
            self.addLink(switchs[18], serveurs[i-1])
            self.addLink(switchs[19], serveurs[i+1])
'''
        # Liaisons entre hôtes et commutateurs
        for i in range(13, 24):
            self.addLink(switchs[i], hotes[i - 13])
            self.addLink(switchs[i], hotes[i - 12])


        for i in range(4):
            self.addLink(switchs[0], switchs[i+1])
        self.addLink(switchs[1], switchs[2])
        self.addLink(switchs[2], switchs[3])
        self.addLink(switchs[3], switchs[4])
        self.addLink(switchs[4], switchs[1])


        for i in range(1, 3):
            self.addLink(switchs[1], switchs[i + 4])
            self.addLink(switchs[2], switchs[i + 6])
            self.addLink(switchs[3], switchs[i + 8])
            self.addLink(switchs[4], switchs[i + 10])
            self.addLink(switchs[5], switchs[i + 12])
            self.addLink(switchs[6], switchs[i + 14])
            self.addLink(switchs[7], switchs[i + 16])
            self.addLink(switchs[8], switchs[i + 18])
            self.addLink(switchs[9], switchs[i + 20])
            self.addLink(switchs[10], switchs[i + 22])
            self.addLink(switchs[11], switchs[i + 24])
            self.addLink(switchs[12], switchs[i + 26])
'''
        for i in range(2):
            self.addLink(switchs[2], switchs[i + 8])
            self.addLink(switchs[3], switchs[i + 10])
            self.addLink(switchs[4], switchs[i + 12])
            self.addLink(switchs[5], switchs[i + 14])
            self.addLink(switchs[6], switchs[i + 16])
            self.addLink(switchs[7], switchs[i + 18])'''


def démarrerRéseau():
    topo = MonTopo()
    c0 = RemoteController('c0', ip='192.168.1.15', port=6653)
    réseau = Mininet(topo=topo, link=TCLink, controller=c0)
    réseau.start()
    CLI(réseau)
    réseau.stop()

if __name__ == '__main__':
    setLogLevel('info')
    démarrerRéseau()

