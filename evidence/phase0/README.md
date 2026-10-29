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
Date: (UK time)
Command:
Run from:
Status: Sanitised
Sanitised by: (what scripts/sanitise.py replaced)
Edited: (only if changed by hand after sanitising, for example versions reduced to major versions)
```

Files from `scripts/phase0-collect.sh` were sanitised with `scripts/sanitise.py`. Tool versions are left out of the header where they would show exact versions.
