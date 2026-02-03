---
trigger: always_on
---

# Error Handling & Logging

## Exception Handling
- **Heirarchy:** Define custom exception classes in `src/domain/exceptions.py`.
    - `MarketSentinelError` (Base)
        - `InsufficientDataError`
        - `APIConnectionError`
        - `SignalGenerationError`
- **Fail Fast:** If critical data is missing (e.g., gaps in intraday data), raise an exception immediately rather than proceeding with corrupted state.
- **Graceful Degradation:** For non-critical failures (e.g., failing to fetch news sentiment), log the error and proceed with technical analysis only if configured to do so.

## Logging
- **Library:** Use the standard `logging` module.
- **Levels:**
    - `DEBUG`: Detailed information for diagnosing problems.
    - `INFO`: Confirmation that things are working as expected (e.g., "Loaded 500 candles").
    - `WARNING`: An indication that something unexpected happened (e.g., "API rate limit approaching").
    - `ERROR`: Due to a more serious problem, the software has not been able to perform some function.
    - `CRITICAL`: A serious error, indicating that the program itself may be unable to continue running.

## Validation
- **Data Sufficiency:** Always validate that execution mode (e.g., `Intraday`) matches the available data quality. Raise `InsufficientDataError` if gaps are found.
