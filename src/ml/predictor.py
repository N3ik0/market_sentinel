import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pandas as pd
import joblib
import os
from src.config.settings import settings

class MarketPredictor:
    """XGBoost based market predictor."""
    
    def __init__(self, model_name: str = "xgboost_generic.pkl"):
        """
        model_name: Name of the file. 
                    If training for a specific ticker, pass 'TSLA.pkl'.
        """
        self.model_path = os.path.join(settings.MODELS_DIR, model_name)
        self.features = []
        
        self.model = xgb.XGBClassifier(
            n_estimators=300,
            max_depth=4,
            learning_rate=0.02,
            subsample=0.8,
            random_state=42,
            objective='multi:softmax', # Multi-class classification
            num_class=3,               # 0 (Neutral), 1 (Long), 2 (Short)
            eval_metric='mlogloss',    # LogLoss for multi-class
            early_stopping_rounds=20   # Stop if no improvement for 20 rounds
        )

    def train(self, df: pd.DataFrame):
        """Train the model."""
        exclude = ['Open', 'High', 'Low', 'Close', 'Volume', 'Target', 'Future_Close', 'Future_Return']
        self.features = [col for col in df.columns if col not in exclude]
        
        X = df[self.features]
        y = df['Target']

        # Time-based split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

        print(f"[*] Training XGBoost on {len(X_train)} rows...")
        
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )

        y_pred = self.model.predict(X_test)
        
        print(f"[+] Global Accuracy: {accuracy_score(y_test, y_pred):.2%}")
        print("\n--- Classification Report ---")
        print(classification_report(y_test, y_pred, target_names=['Neutral', 'Long', 'Short']))
        
        self.save_model()

    def predict(self, features_df: pd.DataFrame) -> int:
        """Predict single instance."""
        return self.model.predict(features_df[self.features])[0]

    def predict_proba(self, features_df: pd.DataFrame) -> float:
        """Returns the probability of the predicted class."""
        probs = self.model.predict_proba(features_df[self.features])[0]
        return max(probs) # Return confidence of winning class

    def save_model(self):
        """Save model to disk."""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump({'model': self.model, 'features': self.features}, self.model_path)
        print(f"[+] Model saved to {self.model_path}")

    def load_model(self):
        """Load model from disk."""
        if os.path.exists(self.model_path):
            data = joblib.load(self.model_path)
            self.model = data['model']
            self.features = data['features']
            print(f"[+] Model loaded from {self.model_path}")
        else:
            print(f"[!] Model file not found: {self.model_path}")

    def get_feature_importance(self):
        """Print feature importance."""
        importances = pd.DataFrame({
            'Feature': self.features,
            'Importance': self.model.feature_importances_
        }).sort_values(by='Importance', ascending=False)
        
        print("\n--- Feature Importance ---")
        print(importances)
