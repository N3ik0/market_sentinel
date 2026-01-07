import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pandas as pd
import joblib
import os

class MarketModel:
    def __init__(self, model_path: str = "models/xgboost_market.pkl"):
        self.model_path = model_path
        self.features = []
        
        # Initialisation du classificateur XGBoost
        # Les paramètres sont ajustés pour un MVP stable
        self.model = xgb.XGBClassifier(
            n_estimators=300,      # Nombre d'arbres
            max_depth=4,           # On réduit un peu la profondeur par rapport au RF
            learning_rate=0.02,    # Pas d'apprentissage : plus c'est petit, plus c'est précis mais lent
            subsample=0.8,         # Utilise 80% des données pour chaque arbre (évite l'overfitting)
            random_state=42,
            eval_metric='logloss'  # Évite les warnings de la bibliothèque
        )

    def train(self, df: pd.DataFrame):
        """Entraîne le modèle XGBoost avec validation temporelle."""
        exclude = ['Open', 'High', 'Low', 'Close', 'Volume', 'Target', 'Target_Price']
        self.features = [col for col in df.columns if col not in exclude]
        
        X = df[self.features]
        y = df['Target']

        # Split temporel strict
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

        print(f"[*] Entraînement XGBoost sur {len(X_train)} jours...")
        
        # XGBoost peut surveiller l'entraînement pour s'arrêter s'il ne progresse plus (Early Stopping)
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )

        y_pred = self.model.predict(X_test)
        
        print(f"[+] Précision globale : {accuracy_score(y_test, y_pred):.2%}")
        print("\n--- Rapport de Classification ---")
        print(classification_report(y_test, y_pred, target_names=['Baisse', 'Hausse']))
        
        self.save_model()

    def save_model(self):
        """Sauvegarde du modèle."""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump({'model': self.model, 'features': self.features}, self.model_path)
        print(f"[+] Modèle sauvegardé dans {self.model_path}")

    def get_feature_importance(self):
        """Analyse l'importance via XGBoost."""
        importances = pd.DataFrame({
            'Feature': self.features,
            'Importance': self.model.feature_importances_
        }).sort_values(by='Importance', ascending=False)
        
        print("\n--- Importance des Indicateurs (XGBoost) ---")
        print(importances)