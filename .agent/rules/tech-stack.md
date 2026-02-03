---
trigger: always_on
---

# Technology Stack

## Core Libraries
- **Language:** Python 3.10+
- **Data Analysis:** `pandas`, `numpy`
- **Technical Analysis:** `pandas-ta` (or `ta-lib` if performance requires)
- **Machine Learning:** `xgboost`, `scikit-learn`
- **API Interface:** `ccxt` (for Crypto), `yfinance` (for generic data), custom wrappers.

## Environment Management
- **Virtual Environment:** strict usage of `venv`.
- **Dependency Management:** `requirements.txt` (or `poetry`/`uv` if migrated).
- **Package Installation:** All packages must be installed directly inside the activated venv.

## Directory Structure
- Follows the Standard Python Project Layout:
    - `src/`: Source code.
    - `tests/`: Tests (mirroring src structure).
    - `notebooks/`: Exploratory Jupyter notebooks.
    - `.agent/rules/`: Agent behavior rules.
