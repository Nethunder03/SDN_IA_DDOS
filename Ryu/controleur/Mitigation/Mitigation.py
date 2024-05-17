from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub

import switch
from datetime import datetime

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix
#from sklearn.metrics import accuracy_score
from sklearn import metrics, preprocessing

class SimpleMonitor13(switch.SimpleSwitch13):

    def __init__(self, *args, **kwargs):

        super(SimpleMonitor13, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)

        start = datetime.now()

        self.flow_training()

        end = datetime.now()
        print("Temps de formation: ", (end-start))

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

            self.flow_predict()

    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        parser = datapath.ofproto_parser

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

 
    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):

        timestamp = datetime.now()
        timestamp = timestamp.timestamp()
        icmp_code = -1
        icmp_type = -1
        tp_src = 0
        tp_dst = 0

        
        file0 = open("Prediction.csv","w")
        file0.write('timestamp,datapath,flow_id,out_port,eth_type,eth_src,eth_dst,ip_src,tp_src,ip_dst,tp_dst,icmp_code,icmp_type,protocol,pktcount,bytecount,flowdur_sec,flowdur_nsec,pktcount_sec,pktcount_nsec,bytecount_sec,bytecount_nsec,label\n')

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


    def flow_training(self):

        self.logger.info("Formation du modèle ...")

        df_ = pd.read_csv('FlowStatsfile.csv')
        df_.dropna(inplace=True)
        df_.drop(['timestamp','datapath','flow_id','in_port','eth_type','eth_src', 'eth_dst', 'ip_src', 'ip_dst'], axis=1, inplace=True)
        df_.ip_proto.unique()
        df_ = pd.get_dummies(df_)
        df_["classe"] = df_["label"]
        del df_["label"]

        scaler = preprocessing.MinMaxScaler()
        df_std= scaler.fit_transform(df_)

        new_df = pd.DataFrame(df_std, columns=df_.columns)
        X = new_df.iloc[:,1:17].astype(float)
        y = new_df.iloc[:,-1]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        
        classifier = KNeighborsClassifier(n_neighbors=5, metric='euclidean', weights ='uniform', p=2)
        self.flow_model = classifier.fit(X_train, y_train)

        y_flow_pred = self.flow_model.predict(X_test)
        #y_flow_pred_train = self.flow_model.predict(X_train)

        self.logger.info("################################################################################")

        self.logger.info("Confusion Matrix")
        cm = confusion_matrix(y_test, y_flow_pred)
        self.logger.info(cm)

       #acc = accuracy_score(y_flow_test, y_flow_pred)

       # acc_train = accuracy_score(y_flow_train, y_flow_pred_train)
       # print("Training Accuracy: ",acc_train)

       # self.logger.info("Succes Accuracy = {0:.2f} %".format(acc*100))
       # fail = 1.0 - acc
       # self.logger.info("Fail Accuracy = {0:.2f} %".format(fail*100))
       # self.logger.info("------------------------------------------------------------------------------")

    def flow_predict(self):
        try:
            predict_dataset = pd.read_csv('Prediction.csv')

            predict_dataset.dropna(inplace=True)
            predict_dataset.drop(['timestamp','datapath','flow_id','in_port','eth_type','eth_src', 'eth_dst', 'ip_src', 'ip_dst'], axis=1, inplace=True)
            predict_dataset.ip_proto.unique()
            predict_dataset = pd.get_dummies(predict_dataset)
            predict_dataset["classe"] = predict_dataset["label"]
            del predict_dataset["label"]

            scaler = preprocessing.MinMaxScaler()
            df_std= scaler.fit_transform(predict_dataset)
            new_df = pd.DataFrame(df_std, columns=predict_dataset.columns)
            X_predict_flow = new_df.iloc[:, :].values
            X_predict_flow = X_predict_flow.astype('float64')
            
            y_flow_pred = self.flow_model.predict(X_predict_flow)

            legitimate_trafic = 0
            ddos_trafic = 0

            for i in y_flow_pred:
                if i == 0:
                    legitimate_trafic = legitimate_trafic + 1
                else:
                    ddos_trafic = ddos_trafic + 1
                    victim = int(predict_dataset.iloc[i, 5])%20
                    
                    
                    

            self.logger.info("------------------------------------------------------------------------------")
            if (legitimate_trafic/len(y_flow_pred)*100) > 80:
                self.logger.info("Traffic is Legitimate!")
            else:
                self.logger.info("NOTICE!! DoS Attack in Progress!!!")
                self.logger.info("Victim Host: h{}".format(victim))
                print("Mitigation process in progress!")
                self.mitigation = 1

            self.logger.info("------------------------------------------------------------------------------")
            
            file0 = open("Prediction.csv","w")
            file0.write('timestamp,datapath,flow_id,out_port,eth_type,eth_src,eth_dst,ip_src,tp_src,ip_dst,tp_dst,icmp_code,icmp_type,protocol,pktcount,bytecount,flowdur_sec,flowdur_nsec,pktcount_sec,pktcount_nsec,bytecount_sec,bytecount_nsec,label\n')
            file0.close()

        except:
            pass
