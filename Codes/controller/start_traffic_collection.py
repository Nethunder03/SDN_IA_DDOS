import switch
from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib.packet import in_proto
from ryu.lib import hub
from operator import attrgetter
import csv
from datetime import datetime
import os

# class CollectTrainingStatsApp(simple_switch_13.SimpleSwitch13):
class CollectTrainingStatsApp(switch.SimpleSwitch13):
    def __init__(self, *args, **kwargs):
        super(CollectTrainingStatsApp, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self.monitor)

        # Vérifiez si le fichier est vide
        self.datapath_data = {}
        self.merged_data = {}
        file0 = open('FlowStatsfile.csv','w')
        file1 = open('PortStatsfile.csv','w')

        file0.write('timestamp,datapath,flow_id,out_port,eth_type,eth_src,eth_dst,ip_src,tp_src,ip_dst,tp_dst,icmp_code,icmp_type,protocol,pktcount,bytecount,flowdur_sec,flowdur_nsec,pktcount_sec,pktcount_nsec,bytecount_sec,bytecount_nsec,label\n')
        file0.close()
        file1.write('timestamp,datapath,rx-pkts,rx-bytes,rx-error,rx_dropped,tx-pkts,tx-bytes,tx-error,tx_dropped,duration_nsec,label\n')
        file1.close()

    #Asynchronous message
    @set_ev_cls(ofp_event.EventOFPStateChange,[MAIN_DISPATCHER, DEAD_DISPATCHER])
    def state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath

        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]


    def monitor(self):
        while True:
            for dp in self.datapaths.values():
                self.request_stats(dp)
            hub.sleep(10)


    def request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)
    
    
    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):

        timestamp = datetime.now()
        timestamp = timestamp.timestamp()
        icmp_code = -1
        icmp_type = -1
        tp_src = 0
        tp_dst = 0
    
        file0 = open("FlowStatsfile.csv","a+")
        body = ev.msg.body
        for stat in sorted([flow for flow in body if (flow.priority == 1) ], key=lambda flow:
            (flow.match['eth_type'],flow.match['ipv4_src'],flow.match['ipv4_dst'],flow.match['ip_proto'])):
            
            ip_src = stat.match['ipv4_src']
            ip_dst = stat.match['ipv4_dst']
            ip_proto = ""
            eth_src = stat.match['eth_src']
            eth_dst = stat.match['eth_dst']
            eth_type = stat.match['eth_type']
            
            if stat.match['ip_proto'] == 1:
                # ICMP
                ip_proto = 'ICMP'
                icmp_code = stat.match['icmpv4_code']
                icmp_type = stat.match['icmpv4_type']

            elif stat.match['ip_proto'] == 6:
                # TCP
                ip_proto = 'TCP'
                tp_src = stat.match['tcp_src']
                tp_dst = stat.match['tcp_dst']

            elif stat.match['ip_proto'] == 17:
                # UDP
                ip_proto = 'UDP'
                tp_src = stat.match['udp_src']
                tp_dst = stat.match['udp_dst']

            flow_id = str(ip_src) + str(tp_src) + str(ip_dst) + str(tp_dst)
                        # Créez une clé unique pour chaque flux

            try:
                pktcount_sec = stat.packet_count / stat.duration_sec
                pktcount_nsec = stat.packet_count / stat.duration_nsec
            except:
                pktcount_sec = 0
                pktcount_nsec = 0

            try:
                bytecount_sec = stat.byte_count / stat.duration_sec
                bytecount_nsec = stat.byte_count / stat.duration_nsec
            except:
                bytecount_sec = 0
                bytecount_nsec = 0

            
            #print(f"Flow Stats Reply: {stat}")
            
            file0.write(f"{timestamp},{ev.msg.datapath.id},{flow_id},{stat.instructions[0].actions[0].port},{eth_type},{eth_src},{eth_dst},{ip_src},{tp_src},{ip_dst},{tp_dst},"
                            f"{icmp_code},{icmp_type},{ip_proto},{stat.packet_count},{stat.byte_count},{stat.duration_sec},{stat.duration_nsec},"
                            f"{pktcount_sec},{pktcount_nsec},{bytecount_sec},{bytecount_nsec},{0}\n")

        file0.close()



    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body
        timestamp = datetime.now()
        timestamp = timestamp.timestamp()

        file1 = open('PortStatsfile.csv','a+')
        for stat in sorted(body, key=attrgetter('port_no')):
            #print(f"Port Stats Reply: {stat}")
            
            file1.write(f"{timestamp},{ev.msg.datapath.id},"
                            f"{stat.rx_packets},{stat.rx_bytes},{stat.rx_errors},{stat.rx_dropped},"
                            f"{stat.tx_packets},{stat.tx_bytes},{stat.tx_errors},{stat.tx_dropped},"
                            f"{stat.duration_sec},{0}\n")

        file1.close()
    
