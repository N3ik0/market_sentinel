---
trigger: always_on
---

# Design Patterns & Best Practices

## Core Principles
1.  **KISS (Keep It Simple, Stupid):** Avoid over-engineering. If a simple function suffices avoiding a complex class hierarchy, use the function.
2.  **DRY (Don't Repeat Yourself):** Abstract common logic into utilities or base classes.
3.  **SOLID:**
    *   **S:** Single Responsibility Principle (One file = One main purpose).
    *   **O:** Open/Closed Principle (Open for extension, closed for modification).
    *   **L:** Liskov Substitution Principle (Subclasses must be substitutable).
    *   **I:** Interface Segregation (Small, specific interfaces).
    *   **D:** Dependency Inversion (Depend on abstractions, not concretions).

## Specific Patterns to Use

### Factory Pattern
*   **Use Case:** Creating `DataLoader` instances based on configuration (e.g., `DataLoaderFactory.get_loader('binance')`).

### Strategy Pattern
*   **Use Case:** Interchangeable algorithms for specific tasks.
    *   *Example:* `TrendDetectionStrategy` (MovingAverage vs. LinearRegression).
    *   *Example:* `EntryStrategy` (Breakout vs. Retest).

### Repository Pattern
*   **Use Case:** Abstracting data access. The app should not know if candles come from a CSV, a Database, or an API.
    *   `CandleRepository.get_latest(symbol, interval)`

### Observer Pattern
*   **Use Case:** Decoupling events.
    *   *Example:* When a `Signal` is generated, notify `RiskManager` and `DiscordNotifier` independently.
