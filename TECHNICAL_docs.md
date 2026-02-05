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
    *   `src/data/` : Gestion sources (Yahoo, Binance).
        *   `factory.py` : Sélection automatique de la source (Crypto -> Binance, Autres -> Yahoo).
        *   `providers/` : Implémentations spécifiques.
    *   `src/models/` : Persistance des modèles (`.pkl`).

---

## 🔄 Pipelines

Il existe trois pipelines principaux, chacun ayant un rôle précis.

### 1. Training Pipeline (`training.py`)
Responsable de la création du modèle prédictif pour un actif donné.

*   **Entrée** : Ticker (ex: `BTCUSD`), Période (ex: `2y` ou `60d`), Mode (Swing/Intraday).
*   **Étapes** :
    1.  Téléchargement historique via **Binance** (avec Pagination pour Intraday) ou Yahoo.
    2.  Génération de features (SMC, Trend, Volatilité) adaptées au timeframe (D1 ou M15).
    3.  Création de la cible (Target) : Classification `Neutral`, `Long`, `Short` basée sur un seuil dynamique (ATR).
    4.  Entraînement du modèle **XGBoost** avec gestion du déséquilibre de classe.
    5.  Sauvegarde du modèle dans `src/models/{TICKER}_{MODE}.pkl`.

### 2. Inference Pipeline (`inference.py`)
Exécuté quotidiennement ou toutes les 15min pour générer des signaux.

*   **Entrée** : Ticker, Mode.
*   **Contrainte ⚠️** : Télécharge automatiquement l'historique nécessaire pour calculer les indicateurs longs (EMA 200).
*   **Étapes** :
    1.  Chargement du modèle `src/models/{TICKER}_{MODE}.pkl`.
    2.  Récupération des données récentes via Binance.
    3.  Calcul des indicateurs (Feature Engineering).
    4.  Prédiction sur la dernière bougie clôturée.
    5.  Filtres :
        *   **Trend Filter** : Vérifie la position du prix vs EMA 200.
        *   **Confidence** : Vérifie si proba > Seuil (ex: 0.65).
    6.  Calcul du plan de trading via `RiskManager` (Stop Loss / R:R).
    7.  Publication sur Notion.

### 3. Backtest Pipeline (`backtest.py`)
Simule la performance de la stratégie sur le passé.

*   **Mode** : Simulation bougie par bougie sur données de test (OOS).
*   **Stratégie d'Exit** : **Trailing Stop** (Suivi de tendance 3x ATR) ou Take Profit fixe.
*   **Rapport** : Génère un rapport de performance (Win Rate, Profit Factor, Drawdown) en console.

---

## 📈 Feature Engineering

La génération d'indicateurs est gérée par `FeatureEngineer` (`src/features/engineering.py`) et déléguée à des modules spécialisés :

### Modules (`src/features/indicators/`)
*   **`momentum.py`** : RSI, Stochastic, MACD, CCI, Williams %R, ROC, Momentum Rank.
*   **`trend.py`** : EMA (20, 50, 200), SMA, Crossovers, Pentes (Slopes), ADX.
*   **`volatility.py`** : ATR, Bollinger Bands (Width, %B), Volatility Rank.
*   **`volume.py`** : Volume SMA, OBV.

### Robustesse
*   **Pagination Binance** : Le provider gère le téléchargement fragmenté pour récupérer l'historique complet (ex: 5000+ bougies 15m) nécessaire à l'entraînement Intraday.

---

## 🤖 Machine Learning

Le moteur est basé sur **XGBoost Classifier**.

*   **Classes** :
    0.  **Neutral** (Wait)
    1.  **Long** (Achat)
    2.  **Short** (Vente)
*   **Stratégie Multi-Mode** :
    *   Un modèle unique est entraîné par Ticker ET par Mode (ex: `BTCUSD_swing.pkl` vs `BTCUSD_intraday.pkl`).
*   **Entraînement** :
    *   **Class Weights** : Pondération automatique pour corriger le ratio Signal/Bruit (ex: Booster l'importance des transactions rares).
    *   Split Temporel (Train sur le passé / Test sur le récent).

---

## 🛡️ Risk Management

Géré par `src/strategy/risk.py` et le pipeline d'exécution.

*   **Logique** : Basée sur l'ATR (Average True Range).
*   **Stop Loss (SL)** : Placé à `X * ATR` du prix d'entrée.
*   **Trailing Stop** : Ajustement dynamique du SL pour sécuriser les gains en tendance.
*   **Position Sizing** : % du capital en risque (ex: 1% ou 2%).
