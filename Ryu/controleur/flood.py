import requests
import json
import csv


# URL de l'API REST de Floodlight pour les statistiques de flux
flow_stats_url = "http://localhost:8080/wm/core/switch/all/flow/json"

# URL de l'API REST de Floodlight pour les statistiques de port
port_stats_url = "http://localhost:8080/wm/core/switch/all/port/json"

try:
    # Récupérer les statistiques de flux
    response_flow = requests.get(flow_stats_url)
    if response_flow.status_code == 200:
        flow_stats = json.loads(response_flow.text)
    else:
        print("Erreur lors de la requête des statistiques de flux :", response_flow.status_code)
        flow_stats = {}

    # Récupérer les statistiques de port
    response_port = requests.get(port_stats_url)
    if response_port.status_code == 200:
        port_stats = json.loads(response_port.text)
    else:
        print("Erreur lors de la requête des statistiques de port :", response_port.status_code)
        port_stats = {}

    # Ouvrir un fichier CSV en écriture
    with open('statistiques_flux_et_port.csv', 'w', newline='') as csvfile:
        fieldnames = ["cookie", "table_id", "packet_count", "byte_count", "idle_timeout_s",
                      "hard_timeout_s", "in_port", "eth_src", "eth_dst", "eth_type", "ipv4_src",
                      "ipv4_dst",

        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Écrire l'en-tête CSV
        writer.writeheader()

        # Parcourir les statistiques de flux et écrire chaque entrée dans le fichier CSV
        for switch, stats in flow_stats.items():
            for flow in stats["flows"]:
                writer.writerow(flow)

    '''        # Parcourir les statistiques de port et écrire chaque entrée dans le fichier CSV
        for switch, stats in port_stats.items():
            for port in stats["port_reply"][0]["port"]:
                writer.writerow(port)'''

    print("Les statistiques de flux et de port ont été enregistrées dans 'statistiques_flux_et_port.csv'.")
except Exception as e:
    print("Une erreur s'est produite :", str(e))
            
            
    '''

            
            "port_number", "receive_packets", "transmit_packets", "receive_bytes",
            "transmit_bytes", "receive_dropped", "transmit_dropped", "receive_errors",
            "transmit_errors", "receive_frame_errors", "receive_overrun_errors",
            "receive_CRC_errors", "collisions", "duration_sec", "duration_nsec", "label",
import requests
import json

# URL de l'API REST de Floodlight pour les statistiques de flux
flow_stats_url = "http://localhost:8080/wm/core/switch/all/flow/json"

# URL de l'API REST de Floodlight pour les statistiques de port
port_stats_url = "http://localhost:8080/wm/core/switch/all/port/json"

# Fonction pour récupérer les statistiques JSON depuis une URL
def get_stats(url):
    response = requests.get(url)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise Exception("Erreur lors de la récupération des statistiques")

try:
    # Récupérer les statistiques de flux
    flow_stats = get_stats(flow_stats_url)
    print("Statistiques de flux :")
    print(json.dumps(flow_stats, indent=4))

    # Récupérer les statistiques de port
    #port_stats = get_stats(port_stats_url)
    #print("\nStatistiques de port :")
    #print(json.dumps(port_stats, indent=4))

except Exception as e:
    print("Une erreur s'est produite :", str(e))

'''