# 🛡️ Market Sentinel - MVP (v1.2 - Active Dev)

> **🚧 PROJET EN ÉVOLUTION CONSTANTE 🚧**
> Ce projet est actuellement en phase de transition majeure vers le trading algorithmique **Crypto Intraday & Swing**. L'architecture et les stratégies sont optimisées quotidiennement.

**Market Sentinel** est un moteur de trading quantitatif modulaire conçu pour le marché des **Cryptomonnaies** (et adaptable aux Actions). Il utilise le Machine Learning (XGBoost) et l'Analyse Technique (SMC, indicateurs) pour détecter des opportunités à haute probabilité.

> **Philosophie :** "Nous ne parions pas, nous tradons des distributions de probabilités."

---

## 🏗️ Architecture Technique

Le projet suit une **Clean Architecture** stricte pour séparer la logique métier de l'infrastructure :

| Couche | Responsabilité | Module |
| :--- | :--- | :--- |
| **Pipelines (App)** | Orchestre les flux complets (Training, Backtest, Inference). | `src.pipelines` |
| **Features (Domain)** | Calcul des indicateurs techniques, Trends (EMA), Volatilité (ATR). | `src.features` |
| **Strategy (Domain)** | Gestion des risques, Stop Loss Trailing, Dimensionnement de position. | `src.strategy` |
| **Machine Learning** | Entraînement et prédiction (XGBoost Classifier). | `src.ml` |
| **Data (Infra)** | Connecteurs boursiers (Binance/CCXT, YFinance) et stockage local. | `src.data` |
| **Interface** | Point d'entrée CLI pour l'utilisateur. | `main.py` |

---

## 📂 Structure du Projet

```bash
market_sentinel/
├── config/                 # Configuration (.env, settings)
├── data/                   # Données brutes et cache (Parquet)
├── src/
│   ├── data/               # Providers (Binance, Yahoo) & Factory
│   ├── features/           # Ingénierie des indicateurs (RSI, ADX, SMC)
│   ├── ml/                 # Moteur de prédiction interactif
│   ├── models/             # Modèles sérialisés (.pkl) par Ticker/Mode
│   ├── pipelines/          # Workflows (Backtest, Training)
│   └── strategy/           # Logique de Risk Management
├── main.py                 # Point d'entrée unique (CLI)
└── requirements.txt        # Dépendances
```

---

## 📊 État Actuel & Objectifs

**Focus Actuel :** BTC/USD & ETH/USD.
**Modes :**
1.  **Swing (D1/W1) :** Capture des grandes tendances (5-10 jours).
2.  **Intraday (M15/H1) :** Trading de volatilité court terme (Scapling/DayTrading).

**Performance (En cours d'optimisation) :**
-   Transition d'un modèle "Actions" vers "Crypto".
-   Intégration récente de : **Filtre de Tendance EMA 200**, **Trailing Stop ATR**, **Gestion de Position Dynamique**.
-   Objectif : Valider un Profit Factor > 1.5 sur l'historique récent (60 jours).

## 🚀 Roadmap Technique
L'objectif est de construire un système autonome et robuste :

### 1. Stratégie & Exécution
*   [x] **Multi-Timeframe** : Analyse conjointe Trend (D1) vs Entry (M15).
*   [x] **Trailing Stop** : Sorties dynamiques pour laisser courir les gains.
*   [ ] **Breakeven** : Sécurisation rapide des trades (Risk Free).
*   **Liquidity & Order Blocks** : Identifier les zones d'accumulation et de distribution institutionnelle.
*   **Volume Profile** : Intégrer la profondeur de marché dans l'apprentissage.

### 2. Évolution de l'IA
*   **Deep Learning** : Transition de XGBoost vers un CNN 1D (Convolutional Neural Network) pour capturer la structure "visuelle" et séquentielle des patterns boursiers.
*   **Analytics** : Développement d'un module analytics.py pour le calcul automatisé du Ratio de Sharpe et du Max Drawdown.

### 3. Scaling & Workflow
*   **Multi-Asset** : Migration vers un scanner multi-actifs (S&P 500 / Nasdaq 100).
*   **Automation** : Automatisation du lien entre le "Journal de Trading" et le "Labo d'Expérience" via Notion Automations.

---

## 🛠️ Installation & Usage

### 1. Installation
```bash
pip install -r requirements.txt
```
*(Assurez-vous d'avoir configuré le fichier `.env`)*

### 2. Entraînement du Modèle
Pour télécharger l'historique et entraîner le modèle :
```bash
# Entraînement en mode SWING (Horizon W1/D1)
python main.py train --ticker BTCUSD

# Entraînement en mode INTRADAY (Horizon H4/H1)
# Note : Le provider Binance télécharge automatiquement jusqu'à ~60j d'historique 15m
python main.py train --ticker BTCUSD --mode intraday
```
Cela génère un fichier `{TICKER}_{mode}.pkl` dans `src/models/`.

### 3. Lancement du Scan (Inférence)
Pour lancer l'analyse en temps réel et publier sur Notion :
```bash
python main.py predict --ticker BTCUSD --mode intraday --threshold 0.65
```

### 4. Backtest (Simulation)
Pour valider la stratégie sur le passé avec les nouvelles options (Filtre de Tendance, Seuil de confiance, etc.) :
```bash
# Backtest Intraday avec Filtre EMA 200 activé et Seuil 0.65
python main.py backtest --ticker BTCUSD --mode intraday --trend_filter --threshold 0.65 --period 60d
```

---

## 🔧 Documentation Technique

Pour aller plus loin et comprendre le fonctionnement interne (Architecture, Pipelines, Calcul des indicateurs), consultez la **[Documentation Technique](TECHNICAL_docs.md)**.

## ❓ Troubleshooting

**Crash lors du `predict` (KeyError...) ?**
Assurez-vous d'avoir téléchargé au moins **2 ans d'historique** (`period="2y"` dans inference.py) car certains indicateurs (comme Volatility Rank 252d) nécessitent 1 an de données minimum pour être calculés. Si l'historique est trop court, l'indicateur est manquant et le modèle crache. Notez que ce correctif a été appliqué dans la version `v1.1`.