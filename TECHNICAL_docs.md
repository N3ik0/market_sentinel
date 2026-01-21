# 📘 Market Sentinel - Documentation Technique

Ce document détaille le fonctionnement interne de **Market Sentinel**. Il est destiné aux développeurs souhaitant comprendre ou étendre le système.

## 🏗️ Architecture Globale

Le projet suit une **Clean Architecture** stricte pour séparer les responsabilités :

1.  **Interface (CLI)** : `main.py` gère les commandes utilisateur (`train`, `predict`, `backtest`).
2.  **Orchestration (Pipelines)** : `src/pipelines/` coordonne le flux de données entre les couches.
3.  **Domaine (Features & Strategy)** :
    *   `src/features/` : Calcul des indicateurs techniques.
    *   `src/strategy/` : Logique de trading (Risk Management).
4.  **Agnostic (ML & Data)** :
    *   `src/ml/` : Wrapper autour de XGBoost.
    *   `src/data/` : Gestion sources (Yahoo) et stockage (Parquet).
    *   `src/models/` : Persistance des modèles (`.pkl`).

---

## 🔄 Pipelines

Il existe trois pipelines principaux, chacun ayant un rôle précis.

### 1. Training Pipeline (`training.py`)
Responsable de la création du modèle prédictif pour un actif donné.

*   **Entrée** : Ticker (ex: `NVDA`), Période (ex: `5y`).
*   **Étapes** :
    1.  Téléchargement historique complet via Yahoo Finance.
    2.  Génération de features (Modular Features + Multi-timeframe).
    3.  Création de la cible (Target) : Classification `Neutral`, `Long`, `Short` basée sur le rendement futur à 5 jours.
    4.  Entraînement du modèle **XGBoost**.
    5.  Sauvegarde du modèle dans `src/models/{TICKER}.pkl`.

### 2. Inference Pipeline (`inference.py`)
Exécuté quotidiennement pour générer des signaux de trading.

*   **Entrée** : Ticker.
*   **Contrainte ⚠️** : Télécharge **2 ans** d'historique minimum.
    *   *Pourquoi ?* Certains indicateurs (ex: `Vol_Rank20d`) nécessitent une fenêtre glissante de 252 jours (1 an de bourse). Une période plus courte entraînerait des valeurs `NaN` et un crash du modèle.
*   **Étapes** :
    1.  Chargement du modèle `src/models/{TICKER}.pkl`.
    2.  Récupération des données récentes (2 ans).
    3.  Calcul des indicateurs (Feature Engineering).
    4.  Prédiction sur la dernière bougie (Dernier jour de clôture).
    5.  Calcul du plan de trading via `RiskManager` (Stop Loss / Take Profit via ATR).
    6.  Publication sur Notion (si configuré).

### 3. Backtest Pipeline (`backtest.py`)
Simule la performance de la stratégie sur le passé.

*   **Mode** : "Walk-Forward" simulé (Note: le modèle actuel est statique, entraîné sur le passé, testé sur le "futur" immédiat du dataset).
*   **Rapport** : Génère un rapport de performance (Win Rate, Profit Factor) en console.

---

## 📈 Feature Engineering

La génération d'indicateurs est gérée par `FeatureEngineer` (`src/features/engineering.py`) et déléguée à des modules spécialisés :

### Modules (`src/features/indicators/`)
*   **`momentum.py`** : RSI, Stochastic, MACD, CCI, Williams %R, ROC, Momentum Rank.
*   **`trend.py`** : EMA, SMA, Crossovers (Golden Cross), Pentes (Slopes), ADX.
*   **`volatility.py`** : ATR, Bollinger Bands (Width, %B), Volatility Rank.
*   **`volume.py`** : Volume SMA, OBV.

### Robustesse
*   **Gestion des `None`** : Les modules vérifient systématiquement si `pandas_ta` retourne un résultat valide avant l'assignation.
*   **Checks de longueur** : Les indicateurs à longue fenêtre (ex: Momentum Rank 5d sur fenêtre 60j, Volatility Rank sur 252j) sont ignorés si l'historique est insuffisant, évitant ainsi de corrompre tout le dataset.

---

## 🤖 Machine Learning

Le moteur est basé sur **XGBoost Classifier**.

*   **Classes** :
    0.  **Neutral** (Wait)
    1.  **Long** (Achat)
    2.  **Short** (Vente)
*   **Stratégie Mono-Asset** :
    *   Un modèle unique est entraîné par Ticker (ex: `NVDA.pkl` est différent de `TSLA.pkl`).
    *   Cela permet de capturer la "personnalité" spécifique de chaque action (volatilité, liquidité).
*   **Entraînement** :
    *   Split Temporel (Train sur le passé / Test sur le récent) pour éviter le *Look-ahead bias*.
    *   Validation set pour le *Early Stopping* (arrête l'entraînement si la performance stagne).

---

## 🛡️ Risk Management

Géré par `src/strategy/risk.py`.

*   **Logique** : Basée sur l'ATR (Average True Range).
*   **Stop Loss (SL)** : Placé à `X * ATR` du prix d'entrée (ajuste le stop selon la volatilité actuelle).
*   **Take Profit (TP)** : Calculé selon un ratio Risque/Rendement (RR) fixe (par défaut 2.0).
*   **Fallback** : Si l'indicateur ATR est manquant, une valeur de repli (2% du prix) est utilisée pour sécuriser le calcul.
