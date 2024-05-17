import requests
import csv
from datetime import datetime
import time  # Ajout du module time

# URL de l'API REST de Floodlight pour les statistiques de flux
flow_stats_url = "http://localhost:8080/wm/core/switch/all/flow/json"

try:
    while True:  # Boucle infinie
        # Récupérer les statistiques de flux depuis l'API REST de Floodlight
        response_flow = requests.get(flow_stats_url)
        if response_flow.status_code == 200:
            flow_stats = response_flow.json()
        else:
            print("Erreur lors de la requête des statistiques de flux :", response_flow.status_code)
            flow_stats = {}

        # Ouvrir un fichier CSV en écriture
        with open('statistiques_flux.csv', 'a', newline='') as csvfile:
            fieldnames = [
                "timestamp", "switch", "eth_src", "eth_dst", "ip_proto", "src_ip", "dst_ip", 
                "tp_src", "tp_dst", "cookie","packet_count", "pktcount_sec", "pktcount_nsec", 
                "byte_count", "bytecount_sec", "bytecount_nsec", "idle_timeout_s", 
                "hard_timeout_s", "in_port", "dur", "dur_nsec", "label",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Écrire l'en-tête CSV (s'il n'existe pas déjà)
            if csvfile.tell() == 0:
                writer.writeheader()

            # Obtenir le timestamp actuel
            timestamp = datetime.now().timestamp()
            tp_src = 0
            tp_dst = 0
            ip_proto = ""
            # Parcourir les statistiques de flux et extraire les adresses IP source et destination
            for switch, stats in flow_stats.items():
                for flow in stats["flows"]:
                    match = flow.get("match", {})
                    if "ipv4_src" in match and "ipv4_dst" in match:
                        
                        if match.get('ip_proto') == '0x6':
                            # TCP
                            ip_proto = 'TCP'
                            tp_src = match.get("tcp_src", "N/A")
                            tp_dst = match.get("tcp_dst", "N/A")

                        elif match.get('ip_proto') == '0x11':
                            # UDP
                            ip_proto = 'UDP'
                            tp_src = match.get("udp_src", "N/A")
                            tp_dst = match.get("udp_dst", "N/A")
                        else:
                            # ICMP
                            ip_proto = 'ICMP'
                            tp_src = 0
                            tp_dst = 0
                        eth_src = match.get("eth_src", "N/A")
                        eth_dst = match.get("eth_dst", "N/A")
                        #eth_type = match.get("eth_type", "N/A")
                        #ip_proto = match.get("ip_proto", "N/A")
                        src_ip = match.get("ipv4_src", "N/A")
                        dst_ip = match.get("ipv4_dst", "N/A")
                        cookie = flow.get("cookie", "N/A")
                        table_id = flow.get("table_id ", "N/A")
                        packet_count = flow.get("packet_count", "N/A")
                        byte_count = flow.get("byte_count", "N/A")
                        idle_timeout_s = flow.get("idle_timeout_s", "N/A")
                        hard_timeout_s = flow.get("hard_timeout_s", "N/A")
                        in_port = match.get("in_port", "N/A")
                        dur = flow.get("duration_sec", "N/A")
                        dur_nsec = flow.get("duration_nsec", "N/A")

                        try:
                            pktcount_sec = float(packet_count)/ float(dur)
                            pktcount_nsec = float(packet_count) / float(dur_nsec)
                        except:
                            pktcount_sec = 0
                            pktcount_nsec = 0

                        try:
                            bytecount_sec = float(byte_count) / float(dur)
                            bytecount_nsec = float(byte_count) / float(dur_nsec)
                        except:
                            bytecount_sec = 0
                            bytecount_nsec = 0

                    writer.writerow({
                        "timestamp": timestamp,
                        "switch": switch,
                        "eth_src": eth_src,
                        "eth_dst": eth_dst,
                        "ip_proto": ip_proto,
                        "src_ip": src_ip,
                        "dst_ip": dst_ip,
                        "tp_src": tp_src,
                        "tp_dst": tp_dst,
                        "cookie": cookie, 
                        "packet_count": packet_count,
                        "pktcount_sec": pktcount_sec,
                        "pktcount_nsec": pktcount_nsec,
                        "byte_count": byte_count,
                        "bytecount_sec": bytecount_sec,
                        "bytecount_nsec": bytecount_nsec,
                        "idle_timeout_s": idle_timeout_s,
                        "hard_timeout_s": hard_timeout_s,
                        "in_port": in_port,
                        "dur": dur,
                        "dur_nsec": dur_nsec,
                        
                        "label": 1
                    })

        print("Les statistiques de flux ont été enregistrées dans 'statistiques_flux.csv'.")
        
        # Attendre quelques secondes avant la prochaine itération
        time.sleep(5)  # Attendre 10 secondes avant de récupérer à nouveau les statistiques

except KeyboardInterrupt:
    print("Arrêt manuel du script.")
except Exception as e:
    print("Une erreur s'est produite :", str(e))
