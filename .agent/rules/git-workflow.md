---
trigger: always_on
---

# Git Workflow

## Commit Messages
- **Conventional Commits:** Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.
    - `feat: add RSI indicator`
    - `fix: resolve API timeout issue`
    - `docs: update architecture diagrams`
    - `refactor: simplify data loading logic`
    - `test: add unit tests for risk manager`

## Branching Stragegy
- **Main:** Stable, production-ready code.
- **Develop:** Integration judge for features.
- **Feature Branches:** `feature/feature-name` (branched from Develop).
- **Hotfix Branches:** `hotfix/bug-name` (branched from Main).

## Pull Requests
- Must pass all tests.
- Requires code review.
- Description must link to the relevant task/issue.
