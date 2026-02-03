---
trigger: always_on
---

# Coding Standards

## Python Style Guide
- **PEP 8:** Follow PEP 8 style guide for all Python code.
- **Docstrings:** Use Google Style Python Docstrings for all functions, classes, and methods.
- **Naming:**
    - `snake_case` for functions and variables.
    - `PascalCase` for classes.
    - `UPPER_CASE` for constants.

## Typing
- **Type Hints:** Python 3.10+ Type Hints are **mandatory** for all function signatures.
- **Strictness:** Aim for `mypy` strict compliance.
- **Financial Types:**
    - Use `Decimal` or `float64` for critical financial calculations to avoid floating-point errors (though `float` is often acceptable for high-speed ML features if precision loss is negligible, be conscious of it).

## Precision & Time
- **Prices:** 
    - **Crypto:** Handle up to 8 decimal places.
    - **Stocks:** Standard 2 decimal places.
- **Timezone:** All internal logic **MUST** be in UTC. Conversion to local time (e.g., `Europe/Paris`) handles only at the very edge (Presentation/Notification layer).

## Imports
- Structure imports in three groups:
    1.  Standard library imports.
    2.  Third-party library imports.
    3.  Local application/library specific imports.
