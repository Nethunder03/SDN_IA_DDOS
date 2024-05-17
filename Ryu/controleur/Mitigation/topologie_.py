#!/usr/bin/python


from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call
import time
import random

def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='172.24.16.0/24')
    hotes = []
    switchs = []
    serveurs = []

    info( '*** Adding controller\n' )

    c0=net.addController(name='c0',
                      controller=RemoteController,
                      ip='192.168.1.14',
                      protocol='tcp',
                      port=6653)


    info( '*** Add switches\n')
    for i in range(1, 14):
            switch= net.addSwitch(f's{i}', cls=OVSKernelSwitch, protocols='OpenFlow13')
            switchs.append(switch)


    info( '*** Add hosts\n')
    for i in range(1, 19):
        mac = ":".join([f"{random.randint(0, 255):02x}" for _ in range(6)])
        hote = net.addHost(f'h{i}', cpu=1.0/20, mac=mac, ip=f'172.24.16.{i}/24', defaultRoute=None)
        hotes.append(hote)

    # Ajout de 4 serveurs
    for i in range(1, 5):
        serveur = net.addHost(f'serv{i}', mac=f'02:a7:00:00:00:0{i*i}', ip=f'172.24.16.{i + 19}/24', defaultRoute=None)
        serveurs.append(serveur)


    info( '*** Add links\n')

        # Liaisons entre hôtes et commutateurs
    #Rack 1
    net.addLink(hotes[0], switchs[4])
    net.addLink(hotes[1], switchs[4])
    net.addLink(hotes[2], switchs[5])
    net.addLink(hotes[3], switchs[5])
    net.addLink(serveurs[0], switchs[5])

    #Rack 2
    net.addLink(hotes[4], switchs[6])
    net.addLink(hotes[5], switchs[6])
    net.addLink(hotes[6], switchs[7])
    net.addLink(hotes[7], switchs[7])
    net.addLink(serveurs[1], switchs[6])

    #Rach 3
    net.addLink(hotes[8], switchs[8])
    net.addLink(hotes[9], switchs[8])
    net.addLink(hotes[10], switchs[9])
    net.addLink(hotes[11], switchs[9])
    net.addLink(serveurs[2], switchs[9])

    net.addLink(hotes[12], switchs[10])
    net.addLink(hotes[13], switchs[10])
    net.addLink(hotes[14], switchs[11])
    net.addLink(hotes[15], switchs[11])
    net.addLink(hotes[16], switchs[12])
    net.addLink(hotes[17], switchs[12])
    net.addLink(serveurs[3], switchs[11])

    # Liaisons entre les commutateurs
    net.addLink(switchs[0], switchs[1])
    net.addLink(switchs[0], switchs[2])
    net.addLink(switchs[0], switchs[3])

    net.addLink(switchs[1], switchs[4])
    net.addLink(switchs[1], switchs[5])
    net.addLink(switchs[1], switchs[6])

    net.addLink(switchs[3], switchs[7])
    net.addLink(switchs[3], switchs[8])
    net.addLink(switchs[3], switchs[9])

    net.addLink(switchs[2], switchs[10])
    net.addLink(switchs[2], switchs[11])
    net.addLink(switchs[2], switchs[12])



    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    for i in range(1, 14): 
        net.get(f's{i}').start([c0])


    #net.pingAll()
    #start server in h5
    #h1 = net.get('h1')
    #cmd1 = "ping 10.10.10.6 &"
    #h1.cmd(cmd1)


    #Generate some random traffic at interval of 10
    
    '''h1 = net.get('h1')
    h2 = net.get('h2')
    h3 = net.get('h3')
    h4 = net.get('h4')
    h5 = net.get('h5')
    h6 = net.get('h6')

    cmd1 = "iperf -u -s &"
    h1.cmd(cmd1)
    h2.cmd(cmd1)
    h3.cmd(cmd1)
    h4.cmd(cmd1)
    h5.cmd(cmd1)
    h6.cmd(cmd1)'''


    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()

