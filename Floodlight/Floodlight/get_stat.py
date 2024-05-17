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
        #print(f" Statistique de flux : {flow_stats}")
    else:
        print("Erreur lors de la requête des statistiques de flux :", response_flow.status_code)
        flow_stats = {}

    # Récupérer les statistiques de port
    response_port = requests.get(port_stats_url)
    if response_port.status_code == 200:
        port_stats = json.loads(response_port.text)
        print(f" Statistique de port : {port_stats}")
    else:
        print("Erreur lors de la requête des statistiques de port :", response_port.status_code)
        port_stats = {}


    # Parcourir les statistiques de port et écrire chaque entrée dans le fichier CSV
    '''for switch, stats in port_stats.items():
        for port in stats["port_reply"][0]["port"]:
            print(f" Statistique de flux : {stats}")'''
    #for switch, stats in flow_stats.items():
        #for flow in stats["flows"]:
        #     if 'ip_proto' in flow["match"]:
        #        print(f" Statistique de port : {stats}")

    print("Les statistiques de flux et de port ont été enregistrées dans 'statistiques_flux_et_port.csv'.")
except Exception as e:
    print("Une erreur s'est produite :", str(e))
