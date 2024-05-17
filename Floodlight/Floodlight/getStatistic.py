import requests
import json
import threading
import time

# Adresse IP et port du contrôleur Floodlight
CONTROLLER_IP = 'localhost'
CONTROLLER_PORT = 8080

# Point de terminaison REST pour les statistiques de flux
FLOW_STATS_ENDPOINT = f'http://{CONTROLLER_IP}:{CONTROLLER_PORT}/wm/core/switch/all/flow/json'

def collect_flow_stats():
    try:
        response = requests.get(FLOW_STATS_ENDPOINT)
        if response.status_code == 200:
            flow_stats = json.loads(response.text)
            for switch_id, stats in flow_stats.items():
                print(f"Switch ID: {switch_id}")
                for flow_entry in stats:
                    print("Flow Entry:")
                    print(stats)
                    '''print(f"  Match: {flow_entry['match']}")
                    print(f"  Packet Count: {flow_entry['packetCount']}")
                    print(f"  Byte Count: {flow_entry['byteCount']}")'''
        else:
            print(f"Failed to fetch flow statistics. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error: {str(e)}")

def async_flow_stats_collection(interval):
    while True:
        collect_flow_stats()
        # Collecte les statistiques de flux à intervalles réguliers
        time.sleep(interval)

if __name__ == '__main__':
    # Créez un thread pour la collecte asynchrone des statistiques de flux
    interval = 10  # Intervalles en secondes
    thread = threading.Thread(target=async_flow_stats_collection, args=(interval,))
    thread.daemon = True  # Le thread se termine lorsque le programme principal se termine
    thread.start()

    # Laissez le programme principal en cours d'exécution pour que le thread de collecte puisse fonctionner
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Arrêt de la collecte des statistiques.")
