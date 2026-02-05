# 🛡️ Market Sentinel - MVP (v1.0)

**Market Sentinel** est un écosystème d'aide à la décision boursière conçu pour éliminer les biais cognitifs via l'analyse quantitative et le Machine Learning. Le système scanne les marchés, entraîne un modèle prédictif et publie des scénarios de trading complets sur Notion.

> **Règle d'or :** "On ne trade que si le modèle confirme un avantage statistique (Edge) > 65%."

---

## 🏗️ Architecture Technique

Le projet a été refactorisé selon une **architecture en couches (Clean Architecture)** pour garantir la scalabilité et la maintenance :

| Couche | Responsabilité | Module |
| :--- | :--- | :--- |
| **Service (Orchestrator)** | Coordonne le flux complet (Scan -> Train -> Publication). | `services.orchestrator` |
| **Domain (Features)** | Transforme les données brutes en indicateurs (SMC, RSI, MACD). | `features.engineering` |
| **Strategy (Risk)** | Applique les règles de gestion du capital (Stop Loss, Take Profit). | `strategy.risk` |
| **Machine Learning** | Gère l'entraînement et la prédiction (XGBoost). | `ml.predictor` |
| **Data Adapter** | Abstraction des sources de données (Yahoo) et du stockage. | `data.providers` / `data.storage` |
| **Infrastructure** | Connecteurs externes (API Notion). | `infrastructure.notion` |
| **Configuration** | Centralisation des variables d'environnement. | `config.settings` |

---

## 📂 Structure du Projet

```bash
market_sentinel/
├── config/                 # Gestion de la configuration (.env)
│   └── settings.py
├── data/                   # Couche d'accès aux données
│   ├── providers/          # Sources externes (Yahoo Finance)
│   └── storage/            # Persistance locale (Parquet)
├── features/               # Logique métier (Indicateurs & SMC)
│   └── engineering.py
├── ml/                     # Moteur d'Intelligence Artificielle
│   └── predictor.py        # Wrapper XGBoost
├── strategy/               # Gestion des risques & Plans de trading
│   └── risk.py
├── infrastructure/         # Services externes
│   └── notion.py           # Client API Notion
├── services/               # Chefs d'orchestre
│   └── orchestrator.py     # Pipeline principal
├── main.py                 # Point d'entrée unique
└── models/                 # Modèles entraînés (.pkl)
```

---

## 📊 État Actuel & Performances
Target : Classification binaire (Up/Down) à horizon 5 jours.

Accuracy : ~65% sur les signaux de hausse (Backtest 5 ans sur NVDA/TSLA).

Infrastructure Cloud : Dashboard temps réel sur Notion (Watchlist, Journal de Trading, Labo d'expérience).

## 🚀 Roadmap pour Optimisation (Next Steps)
L'objectif est de passer d'un modèle tabulaire simple à un système de reconnaissance de Patterns Smart Money Concepts (SMC) :

### 1. Feature Engineering Avancé
*   **Fair Value Gaps (FVG)** : Coder la détection mathématique des déséquilibres de prix (Imbalances).
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