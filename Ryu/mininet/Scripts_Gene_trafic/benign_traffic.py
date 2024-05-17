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
    ip = ".".join(["172","24","16",str(randrange(1,19))])
    return ip
        
def startNetwork():
    topo = MyTopo()
    c0 = RemoteController('c0', ip='192.168.1.12', port=6653)
    net = Mininet(topo=topo, link=TCLink, controller=c0)

    net.start()
    hote_rec = []
    
    for i in range(1, 19):
        nom_hote = f'h{i}'
        objet_hote = net.get(nom_hote)
        hote_rec.append(objet_hote)
    
    print(f"*=*=" * 15 + "*\n"
        f"*                  Génération du trafic...                  *\n" +
        f"*=*=" * 15 +"*\n")
  
    hote_rec[0].cmd('cd /home/mininet/serveurweb')
    hote_rec[0].cmd('python -m SimpleHTTPServer 80 &')
    hote_rec[0].cmd('iperf -s -p 5050 &')
    hote_rec[0].cmd('iperf -s -u -p 5051 &')
    sleep(2)
    hote_rec[10].cmd('cd /home/mininet/serveurweb')
    hote_rec[10].cmd('python -m SimpleHTTPServer 80 &')
    hote_rec[10].cmd('iperf -s -p 5050 &')
    hote_rec[10].cmd('iperf -s -u -p 5051 &')
    sleep(2)
    for h in hote_rec:
        h.cmd('cd /home/mininet/Downloads')
    for i in range(600):

        print(f"*=*=" * 15 + "*\n"
            f"*    {i + 1}    *          Itération num : {i + 1}        *   {i + 1}         *\n" +
            f"*=*=" * 15 +"*")
        
        for j in range(10):
            src = choice(hote_rec)
            dst = ip_generator()
            
            if j <9:
                print("génération du trafic ICMP entre %s et h%s et du trafic TCP/UDP entre %s et h1 et h11" % (src,((dst.split('.'))[3]),src))
                src.cmd(f"ping {dst} -c 100 &")
                src.cmd("iperf -p 5050 -c 172.24.16.1")
                src.cmd("iperf -p 5051 -u -c 172.24.16.1")
                src.cmd("iperf -p 5050 -c 172.24.16.11")
                src.cmd("iperf -p 5051 -u -c 172.24.16.11")
            else:
                print("génération du trafic ICMP entre %s et h%s et du trafic TCP/UDP entre %s et h11 et h1" % (src,((dst.split('.'))[3]),src))
                src.cmd(f"ping {dst} -c 100 &")
                src.cmd("iperf -p 5050 -c 172.24.16.11")
                src.cmd("iperf -p 5051 -u -c 172.24.16.11")
                src.cmd("iperf -p 5050 -c 172.24.16.1")
                src.cmd("iperf -p 5051 -u -c 172.24.16.1")
            
            print(f"{src} Téléchargement de index.html depuis h1")
            src.cmd("wget http://172.24.16.21/index.html")
            print(f"{src} Téléchargement de test.zip depuis h1")
            src.cmd("wget http://172.24.16.1/test.zip")
            print(f"{src} Téléchargement de index.html depuis h1")
            src.cmd("wget http://172.24.16.11/index.html")
            print(f"{src} Téléchargement de test.zip depuis h1")
            src.cmd("wget http://172.24.16.11/test.zip")
        
        hote_rec[0].cmd("rm -f *.* /home/mininet/Downloads")
        
    print(f"*-*-" * 15 + "*")
    
    net.stop()

if __name__ == '__main__':
    
    debut = datetime.now()
    setLogLevel( 'info' )
    startNetwork()
    fin = datetime.now()
    print(fin-debut)