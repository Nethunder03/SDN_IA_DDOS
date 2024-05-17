
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.node import OVSKernelSwitch, RemoteController

class MyTopology(Topo):
    def build(self):
        # Création des commutateurs
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        switch3 = self.addSwitch('s3')

        # Création des hôtes
        host1 = self.addHost('h1')
        host2 = self.addHost('h2')
        host3 = self.addHost('h3')
        host4 = self.addHost('h4')
        host5 = self.addHost('h5')
        host6 = self.addHost('h6')
        host7 = self.addHost('h7')
        host8 = self.addHost('h8')
        host9 = self.addHost('h9')

        # Connexions des hôtes aux commutateurs
        self.addLink(host1, switch1)
        self.addLink(host2, switch1)
        self.addLink(host3, switch2)
        self.addLink(host4, switch2)
        self.addLink(host5, switch2)
        self.addLink(host6, switch3)
        self.addLink(host7, switch3)
        self.addLink(host8, switch3)
        self.addLink(host9, switch3)
        self.addLink(switch1, switch3)
        self.addLink(switch1, switch2)

def démarrerRéseau():
    topo = MyTopology()
    c0 = RemoteController('c0', ip='192.168.1.4', port=6653)
    réseau = Mininet(topo=topo, link=TCLink, controller=c0)
    réseau.start()
    CLI(réseau)
    réseau.stop()

if __name__ == '__main__':
    setLogLevel('info')
    démarrerRéseau()



