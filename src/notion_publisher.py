import requests
from datetime import datetime
import pytz # Importation pour gérer les fuseaux horaires

class NotionPublisher:
    def __init__(self, token: str, database_id: str):

        """

        Initialise la connexion à l'API Notion.

        token: Le secret d'intégration interne.

        database_id: L'ID de la base Market Sentinel.

        """

        self.token = token

        self.database_id = database_id

        self.headers = {

            "Authorization": f"Bearer {self.token}",

            "Content-Type": "application/json",

            "Notion-Version": "2022-06-28"

    } 

    def publish_plan(self, plan: dict, confidence: float):
        url = "https://api.notion.com/v1/pages"
        
        # Récupération de l'heure précise de Paris
        paris_tz = pytz.timezone("Europe/Paris")
        now_paris = datetime.now(paris_tz)
        
        payload = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Ticker (ex: Alphabet, Apple)": {
                    "title": [{"text": {"content": plan['ticker']}}]
                },
                "Signal": {
                    "select": {"name": plan['direction']}
                },
                "Confiance": {
                    "number": round(confidence, 2)
                },
                "Prix d'entrée": {
                    "number": plan['entry']
                },
                "Stop-Loss": {
                    "number": plan['sl']
                },
                "Take-Profit": {
                    "number": plan['tp']
                },
                "Date du Scan": {
                    "date": {"start": now_paris.isoformat()}
                },
                "Sentinel Score": {
                    "number": plan['rr_ratio']
                }
            }
        }

        response = requests.post(url, json=payload, headers=self.headers)
        
        print(f"[*] Statut API : {response.status_code}")
        if response.status_code != 200:
            print(f"[!] Détail de l'erreur : {response.text}")
        else:
            print(f"[+] Succès ! Ligne créée dans Notion (Heure Paris).")