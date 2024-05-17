from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
import time

import switch
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report
import pickle
import pandas as pd
import numpy as np

# ...
class SimpleMonitor13(switch.SimpleSwitch13):

    def __init__(self, *args, **kwargs):

        super(SimpleMonitor13, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)
        #with open('modele_dt.pickle', 'rb') as model_file:
        #    self.loaded_model = pickle.load(model_file)

        start = datetime.now()
        end = datetime.now()
        self.flow_training()
        print("Training time: ", (end-start))
        


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

        # Inside your loop
        file0 = open("Prediction.csv","w")
        file0.write('timestamp,datapath,flow_id,in_port,eth_type,eth_src,eth_dst,ip_src,tp_src,ip_dst,tp_dst,icmp_code,icmp_type,protocol,pktcount,bytecount,flowdur_sec,flowdur_nsec,pktcount_sec,pktcount_nsec,bytecount_sec,bytecount_nsec\n')
        
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
                            f"{pktcount_sec},{pktcount_nsec},{bytecount_sec},{bytecount_nsec}\n")

        file0.close()


    def flow_training(self):

        self.logger.info("Flow Training ...")

        df = pd.read_csv('FlowStatsfile.csv')
        df.dropna(inplace=True)

        # Supprimer les colonnes non nécessaires
        df.drop(['timestamp', 'datapath', 'flow_id', 'in_port', 'eth_type', 'eth_src', 'eth_dst', 'ip_src', 'ip_dst', 'protocol'], axis=1, inplace=True)

        # Afficher les valeurs uniques de la colonne 'protocol'
        #print(df.protocol.unique())

        df['class'] = df['label']
        del df['label']

        # Normalisation Min-Max de toutes les caractéristiques numériques
        scaler = MinMaxScaler()
        df_nrm = scaler.fit_transform(df)
        df_nv = pd.DataFrame(df_nrm, columns=df.columns)


        X = df_nv.drop('class', axis=1).astype(float)
        y = df_nv['class']

        X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
        X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

        start_time = time.time()
        
        dt_classifier = DecisionTreeClassifier()

        # Recherche des hyperparamètres optimaux
        param_grid = {
            'criterion': ['gini', 'entropy', 'log_loss'],
            'max_depth': [None, 2, 3, 4, 5],
            'max_leaf_nodes': [2, 3, 4, 5]
        }

        dt_search = GridSearchCV(dt_classifier, param_grid=param_grid, n_jobs=-1, cv=5, scoring='accuracy', verbose=2)
        dt_search.fit(X_train, y_train)

        criterion = dt_search.best_params_['criterion']
        max_depth = dt_search.best_params_['max_depth']
        max_leaf_nodes = dt_search.best_params_['max_leaf_nodes']

        # Entraînement du modèle avec les hyperparamètres optimaux
        dt_classifier = DecisionTreeClassifier(criterion=criterion, max_depth=max_depth, max_leaf_nodes=max_leaf_nodes)
        self.dt_classif = dt_classifier.fit(X_train, y_train)

        # Prédiction et évaluation sur l'ensemble de validation
        predicted_val = self.dt_classif.predict(X_val)
        accuracy_val = accuracy_score(y_val, predicted_val)
        print(f"Précision sur l'ensemble de validation : {round(accuracy_val * 100, 2)}%")


        # Prédiction et évaluation du modèle
        predicted_dt = self.dt_classif.predict(X_test)
        accuracy_dt = accuracy_score(y_test, predicted_dt)

        # Stockage des résultats
        results = {
            'criterion': criterion,
            'max_depth': max_depth,
            'max_leaf_nodes': max_leaf_nodes,
            'accuracy': round(accuracy_dt * 100, 2)
        }

        # Affichage des résultats
        print(f"criterion: {criterion}, max depth: {max_depth}, max_leaf: {max_leaf_nodes}")
        print(f"La précision est : {results['accuracy']}%")
        print("########################################################################")
        print(classification_report(predicted_dt, y_test))
        print("########################################################################")

        print("--- %s secondes --- temps pour l'arbre de décision " % (time.time() - start_time))


    def flow_predict(self):
        try:
            # Charger le fichier CSV
            df = pd.read_csv('Prediction.csv')
            dfv = df.copy()
            df.dropna(inplace=True)
            df.drop(['timestamp', 'datapath', 'flow_id', 'in_port', 'eth_type', 'eth_src', 'eth_dst', 'ip_src', 'ip_dst', 'protocol',], axis=1, inplace=True)

            # Normalisation Min-Max de toutes les caractéristiques numériques
            scaler = MinMaxScaler()
            df_nrm = scaler.fit_transform(df)
            df_nv = pd.DataFrame(df_nrm, columns=df.columns)
            
            y_flow_pred = self.dt_classif.predict(df_nv)


            # Initialiser les compteurs pour le trafic légitime et le trafic DDoS
            legitimate_traffic = 0
            ddos_traffic = 0

            # Initialiser la variable pour le numéro de la victime
            victim = None

            # Analyser les prédictions
            for index, prediction in enumerate(y_flow_pred):
                if prediction == 0:
                    legitimate_traffic += 1
                else:
                    ddos_traffic += 1
                    victim = int(dfv.iloc[index, 5]) % 20

            # Analyse des résultats
            if (legitimate_traffic / len(y_flow_pred) * 100) > 80:
                self.logger.info("Traffic is Legitimate!")
            else:
                self.logger.info("NOTICE!! DoS Attack in Progress!!!")
                if victim is not None:
                    self.logger.info("Victim Host: h{}".format(victim))
                print("Mitigation process in progress!")
                self.mitigation = 1
    
            file0 = open("Prediction.csv","w")
            file0.write('timestamp,datapath,flow_id,in_port,eth_type,eth_src,eth_dst,ip_src,tp_src,ip_dst,tp_dst,icmp_code,icmp_type,protocol,pktcount,bytecount,flowdur_sec,flowdur_nsec,pktcount_sec,pktcount_nsec,bytecount_sec,bytecount_nsec\n')
            file0.close()

        except Exception as e:
            print(f"An error occurred: {e}")

            
