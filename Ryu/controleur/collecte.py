import switch
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
import csv
from datetime import datetime


class CollectTrainingStatsApp(switch.SimpleSwitch13):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self.monitor)
        self.fieldnames = [
            'timestamp', 'dt', 'switch', 'src', 'dst', 'pktcount', 'bytecount', 'dur', 'dur_nsec',
            'tot_dur', 'flows', 'packetins', 'pktperflow', 'byteperflow', 'pktrate', 'Pairflow',
            'Protocol', 'port_no', 'tx_bytes', 'rx_bytes', 'tx_kbps', 'rx_kbps', 'tot_kbps', 'label'
        ]
        self.filename = "FlowStatsfile.csv"
        self.initialize_csv_file()
        self.flow_count = {}
    
    def initialize_csv_file(self):
        with open(self.filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writeheader()

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug(f'Enregistrement du datapath : {datapath.id:016x}' )
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug(f"Désenregistrement du datapath : {datapath.id:016x}")
                del self.datapaths[datapath.id]

    def monitor(self):
        while True:
            for dp in self.datapaths.values():
                self.request_stats(dp)
            hub.sleep(10)

    def request_stats(self, datapath):
        self.logger.debug(f"Envoi de la demande de statistiques : {datapath.id:016x}")
        parser = datapath.ofproto_parser
        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)


    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def flow_stats_reply_handler(self, ev):
        timestamp = datetime.now().timestamp()
        timestamp = timestamp
        with open(self.filename, "a+") as file0:
            body = ev.msg.body
            for stat in sorted([flow for flow in body if flow.priority == 1], key=lambda flow: (flow.match['eth_type'], flow.match['ipv4_src'], flow.match['ipv4_dst'], flow.match['ip_proto'])):
                if stat.match['eth_type'] == ether_types.ETH_TYPE_IP:
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

                
                
                
                src, dst = self.calculate_src_dst(stat)
                flows = self.calculate_flows(stat)
                pktperflow = self.calculate_pktperflow(stat)
                Pairflow = self.calculate_Pairflow(stat)
                label = self.calculate_label(stat)
                tx_kbps, rx_kbps, tot_kbps = self.calculate_kbps(stat.port_no, stat.tx_bytes, stat.rx_bytes)





if stat.match['eth_type'] == ether_types.ETH_TYPE_IP:
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
