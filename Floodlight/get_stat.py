import requests
import json


def get_flow_stats(dp_id):
    url = 'http://localhost:8080/wm/core/switch/{}/flow/statistics'.format(dp_id)
    headers = {'Content-Type': 'application/json'}
    payload = {'match': {}}

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()


def get_port_stats(dp_id):
    url = 'http://localhost:8080/wm/core/switch/{}/port/statistics'.format(dp_id)
    headers = {'Content-Type': 'application/json'}
    payload = {'match': {}}

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()


def main():
    # Obtenez la liste de tous les commutateurs
    url = 'http://localhost:8080/wm/core/switch'
    response = requests.get(url)

    # Vérifiez si la réponse contient une clé `switches`
    if 'switches' not in response.json():
        print('Le contrôleur Floodlight ne répond pas.')
        return

    switches = response.json()['switches']

    # Parcourez tous les commutateurs et affichez les données à l'écran
    for switch in switches:
        flow_stats = get_flow_stats(switch['id'])
        port_stats = get_port_stats(switch['id'])

        # Affichez les statistiques de flux
        print('Statistiques de flux pour le commutateur {}'.format(switch['id']))
        for stat in flow_stats['stats']:
            print('{}: {}'.format(stat['stat_type'], stat['value']))

        # Affichez les statistiques de port
        print('Statistiques de port pour le commutateur {}'.format(switch['id']))
        for stat in port_stats['stats']:
            print('{}: {}'.format(stat['stat_type'], stat['value']))


if __name__ == '__main__':
    main()
