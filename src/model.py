from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pandas as pd

class MarketModel:
    def __init__(self):
        # Initialisation de la "forêt" avec 100 arbres de décision
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.features = []
    
    def train(self, df: pd.DataFrame):
        """ Entrainement du modèle sur le dataset fourni """

        # 1. Selection des colonnes d'entrée, retire prix et target
        # Ne garde que les indicateurs mathématiques
        exclude = ['Open', 'High', 'Low', 'Close', 'Volume', 'Target', 'Target_Price']
        self.features = [col for col in df.columns if col not in exclude]

        X = df[self.features] # Entrées (rsi, ema, etc.)
        y = df['Target'] # Réponse 0 ou 1

        # Séparation : 80/20 apprentissage/test si l'ia a raison
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

        # 3. Apprentissage
        print(f"[*] Entraînement sur {len(X_train)} échantillons...")
        self.model.fit(X_train, y_train)

        # 4. Évaluation
        y_pred = self.model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        
        print(f"[+] Précision du modèle : {acc:.2%}")
        return acc