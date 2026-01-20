import requests
from datetime import datetime
import pytz
from typing import Dict, Any

class NotionClient:
    """Interacts with Notion API."""
    
    def __init__(self, token: str, database_id: str):
        self.token = token
        self.database_id = database_id
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def publish_trading_plan(self, plan: Dict[str, Any], confidence: float):
        """Creates a page in the trading journal database."""
        url = "https://api.notion.com/v1/pages"
        
        # Paris Time
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

        try:
            response = requests.post(url, json=payload, headers=self.headers)
            print(f"[*] Notion API Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"[!] Notion Error: {response.text}")
            else:
                print(f"[+] Success! Plan published to Notion.")
                
        except Exception as e:
            print(f"[!] Network error publishing to Notion: {e}")
