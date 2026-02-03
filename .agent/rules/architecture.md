---
trigger: always_on
---

# Architecture Principles

## High-Level Architecture
The project follows a **Modular Layered Architecture** (inspired by Clean Architecture/Onion Architecture) to ensure separation of concerns and testability.

### Layers
1.  **Domain/Core:** Financial logic, pure entities (Trade, Candle, Indicator), and interfaces. *No external dependencies.*
2.  **Application:** Use cases (e.g., `RunBacktest`, `ExecuteTrade`). Orchestrates the domain objects.
3.  **Infrastructure:** Implementation of interfaces (DataLoaders, API Clients, Database Adapters).
4.  **Interface/Presentation:** CLI entry points, specialized scripts (`main.py`).

## Modularity & Extensibility
*   **Asset Class Agnostic Core:** The core logic (Signal generation, Risk Management) should act on generic `Asset` or `Instrument` interfaces.
*   **Asset Class Implementation:** 
    *   **Current Active Module:** `Crypto` (Binance/Bybit adaptors, 24/7 logic).
    *   **Future Modules:** `Forex`, `Stocks` (to be implemented later via the same interfaces).

## Dependency Rule
Dependencies must point **inwards**.
*   `Infrastructure` depends on `Domain`.
*   `Domain` depends on NOTHING.
*   `main.py` (Composition Root) wires everything together.

## File Structure (`src/`)
*   `src/domain/`: Entities and Interfaces.
*   `src/application/`: Orchestration logic.
*   `src/infrastructure/`: Concrete implementations (API calls, DB).
*   `src/interfaces/`: CLI commands.
