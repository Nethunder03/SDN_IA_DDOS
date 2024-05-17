#encoding: utf-8
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.node import OVSKernelSwitch, RemoteController
from random import randrange
from mininet.util import dumpNodeConnections




class MyTopo(Topo):
    def build(self):

        S1, S2, S3= 4, 10, 10

        Core, Aggregation, Edge= [], [], []

        # Ajout des switches core
        for i in range(S1):
            switch = self.addSwitch(f'SC{i + 1}', cls=OVSKernelSwitch, protocols='OpenFlow13')
            Core.append(switch)

        # Ajout des switches de distibution
        for i in range(S2):
            switch = self.addSwitch(f'SD{S1 + i + 1}', cls=OVSKernelSwitch, protocols='OpenFlow13')
            Aggregation.append(switch)

        # Ajout des switches d'acces
        for i in range(S3):
            switch = self.addSwitch(f'SE{S1 + S2 + i + 1}', cls=OVSKernelSwitch, protocols='OpenFlow13')
            Edge.append(switch)

        # Ajout de liens entre les commutateurs core et de distribution
        for i in range(S1):
            sw1 = Core[i]
            for sw2 in Aggregation[i // 2::S1 // 2]:
                self.addLink(sw2, sw1)

        # Ajout de liens entre les commutateurs de distribution et d'acces
        for i in range(0, S2, 2):
            for sw1 in Aggregation[i:i + 2]:
                for sw2 in Edge[i:i + 2]:
                    self.addLink(sw2, sw1)

        # Add hosts and their links with edge switches
        count = 1
        for sw1 in Edge[:8]:
            for i in range(3):
                mac = ":".join([f"{randrange(256):02x}" for _ in range(6)])
                host = self.addHost(f'h{count}', cpu=1.0/20, mac=mac, ip=f'172.24.16.{count}/24')
                self.addLink(sw1, host)
                count += 1

        # Ajout de 4 serveurs connectés aux nouveaux switches Edge
        count = 25  
        for sw1 in Edge[8:]:
            for i in range(2):
                mac = ":".join([f"{randrange(256):02x}" for _ in range(6)])
                server = self.addHost(f'server{count}', cpu=1.0/20, mac=mac, ip=f'172.24.16.{count}/24')
                self.addLink(sw1, server)
                count += 1

def démarrerRéseau():
    topo = MyTopo()
    c0 = RemoteController('c0', ip='192.168.1.14', port=6653)
    réseau = Mininet(topo=topo, link=TCLink, controller=c0)
    réseau.start()
    CLI(réseau)
    réseau.stop()

if __name__ == '__main__':
    setLogLevel('info')
    démarrerRéseau()
