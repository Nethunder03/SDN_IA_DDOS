import re
import csv
from datetime import datetime

# Chemin vers le fichier journal du contrôleur Floodlight
log_file_path = "/chemin/vers/le/fichier/journal.log"

try:
    # Ouvrir le fichier journal en lecture
    with open(log_file_path, "r") as log_file:
        packetins_data = []

        # Parcourir chaque ligne du fichier journal
        for line in log_file:
            # Utilisez une expression régulière pour extraire les statistiques "packetins"
            match = re.search(r'packetins: (\d+)', line)
            if match:
                packetins_count = int(match.group(1))
                packetins_data.append(packetins_count)

        # Ouvrir un fichier CSV en écriture pour enregistrer les statistiques "packetins"
        with open('statistiques_packetins.csv', 'w', newline='') as csvfile:
            fieldnames = ["timestamp", "packetins"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Obtenir le timestamp actuel
            timestamp = datetime.now().timestamp()

            # Écrire les statistiques "packetins" dans le fichier CSV
            for packetins_count in packetins_data:
                writer.writerow({"timestamp": timestamp, "packetins": packetins_count})

    print("Les statistiques 'packetins' ont été enregistrées dans 'statistiques_packetins.csv'.")
except Exception as e:
    print("Une erreur s'est produite :", str(e))
