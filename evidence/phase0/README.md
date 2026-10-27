# Phase 0 evidence

Sanitised evidence for the Phase 0 baseline tests in [05-verification.md](../../docs/05-verification.md), section 4.

## Rules

- Sanitised files only. Raw output stays outside the repository and is never committed
- One file per test, named `V-xx_short-description.ext`, for example `V-01_tcp-scan.txt`
- Apply the sanitisation checklist in 05-verification.md, section 2.4, before every commit

## File header

Each evidence file starts with:

```
Test ID:
Date:
Command or tool and version:
Run from:
Sanitised by: (what was replaced or removed)
```
