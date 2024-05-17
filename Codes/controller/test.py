import switch
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib import dpid as dpid_lib
from ryu.lib import stplib
from ryu.lib.packet import in_proto
from ryu.lib.packet import ipv4
from ryu.lib.packet import icmp
from ryu.lib.packet import tcp
from ryu.lib.packet import udp
from ryu.lib.packet import arp
from operator import attrgetter
import csv
from datetime import datetime
import os

            
# class CollectTrainingStatsApp(simple_switch_13.SimpleSwitch13):
class CollectTrainingStatsApp(switch.SimpleSwitch13):
    def __init__(self, *args, **kwargs):
            super(CollectTrainingStatsApp, self).__init__(*args, **kwargs)
            self.datapaths = {}
            self.monitor_thread = hub.spawn(self._monitor)
            
            
            # Vérifiez si le fichier est vide
            self.datapath_data = {}
            file_empty = os.stat('merged_data.csv').st_size == 0

            # Ouvrez un fichier CSV en mode ajout
            with open('merged_data.csv', 'a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)

                # Si le fichier est vide, écrivez l'en-tête
                if file_empty:
                    csv_writer.writerow(['timestamp', 'datapath', 'flow_id', 'out_port', 'ip_src', 'tp_src', 'ip_dst',
                                        'tp_dst', 'icmp_code', 'icmp_type', 'ip_proto',
                                        'pktcount', 'bytecount', 'flowdur_sec', 'flowdur_nsec', 'pktcount_sec',
                                        'pktcount_nsec',
                                        'bytecount_sec', 'bytecount_nsec',
                                        'port', 'rx-pkts', 'rx-bytes', 'rx-error', 'tx-pkts', 'tx-bytes', 'tx-error',
                                        'label'])
    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(10)

    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)


    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        body = ev.msg.body
        timestamp = datetime.now()
        timestamp = timestamp.timestamp()
        icmp_code = -1
        icmp_type = -1
        tp_src = 0
        tp_dst = 0

        for stat in sorted([flow for flow in body if (flow.priority == 1)],
                           key=lambda flow: (flow.match['in_port'],
                                             flow.match['eth_dst'],flow.match['eth_type'],
                                             flow.match['ipv4_src'], flow.match['ipv4_dst'],
                                             flow.match['ip_proto'])):
            self.logger.info('%016x %8x %17s %8x %8d %8d',
                             ev.msg.datapath.id,
                             stat.match['in_port'], stat.match['eth_dst'],
                             stat.instructions[0].actions[0].port,
                             stat.packet_count, stat.byte_count)

            datapath_id = ev.msg.datapath.id

            if 'ipv4_src' in stat.match and 'ipv4_dst' in stat.match:
                ip_src = stat.match['ipv4_src']
                ip_dst = stat.match['ipv4_dst']

                if 'ip_proto' in stat.match:
                    if stat.match['ip_proto'] == in_proto.IPPROTO_ICMP:
                        # ICMP
                        ip_proto = 'ICMP'
                        icmp_code = stat.match['icmpv4_code']
                        icmp_type = stat.match['icmpv4_type']
                    elif stat.match['ip_proto'] == in_proto.IPPROTO_TCP:
                        # TCP
                        ip_proto = 'TCP'
                        tp_src = stat.match['tcp_src']
                        tp_dst = stat.match['tcp_dst']
                    elif stat.match['ip_proto'] == in_proto.IPPROTO_UDP:
                        # UDP
                        ip_proto = 'UDP'
                        tp_src = stat.match['udp_src']
                        tp_dst = stat.match['udp_dst']

            # Créez une clé unique pour chaque flux
            flow_key = (
                datapath_id,
                stat.match['in_port'], 
                stat.match['eth_dst'],
                stat.match['ipv4_src'],
                stat.match['ipv4_dst'],
                stat.instructions[0].actions[0].port
            )
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

            flow_id = str(ip_src) + str(tp_src) + str(ip_dst) + str(tp_dst)
            # Récupérez les données existantes

            data = self.datapath_data.get(flow_key, {
                'timestamp': timestamp,
                'datapath': datapath_id,
                'flow_id': flow_id,
                'out_port': stat.instructions[0].actions[0].port,
                'ip_src': ip_src,
                'tp_src': tp_src,
                'ip_dst': ip_dst,
                'tp_dst': tp_dst,
                'icmp_code': icmp_code,
                'icmp_type': icmp_type,
                'ip_proto': ip_proto,
                'pktcount': stat.packet_count,
                'bytecount': stat.byte_count,
                'flowdur_sec': stat.duration_sec,
                'flowdur_nsec': stat.duration_nsec,
                'pktcount_sec': pktcount_sec,
                'pktcount_nsec': pktcount_nsec,
                'bytecount_sec': bytecount_sec,
                'bytecount_nsec': bytecount_nsec,
                'port': None,
                'rx-pkts': None,
                'rx-bytes': None,
                'rx-error': None,
                'tx-pkts': None,
                'tx-bytes': None,
                'tx-error': None,
                'label': None
            })

            # Stockez les données mises à jour dans le dictionnaire
            self.datapath_data[flow_key] = data
            print(self.datapath_data)
            # Si toutes les informations sont disponibles, écrivez-les dans le fichier CSV
            if all(data.values()):
                with open('merged_data.csv', 'a', newline='') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    csv_writer.writerow(list(data.values()))
                    '''

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.info('datapath         port     '
                         'rx-pkts  rx-bytes rx-error '
                         'tx-pkts  tx-bytes tx-error')
        self.logger.info('---------------- -------- '
                         '-------- -------- -------- '
                         '-------- -------- --------')
        for stat in sorted(body, key=attrgetter('port_no')):
            self.logger.info('%016x %8x %8d %8d %8d %8d %8d %8d',
                             ev.msg.datapath.id, stat.port_no,
                             stat.rx_packets, stat.rx_bytes, stat.rx_errors,
                             stat.tx_packets, stat.tx_bytes, stat.tx_errors)'''