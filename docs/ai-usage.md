# AI Usage

> **Status:** Draft v0.6 · Last updated: 27th October 2026
> **Author:** William Drummond
> **Related:** [04-design-decisions.md](04-design-decisions.md) · [05-verification.md](05-verification.md)

---

## 1. Purpose

This document discloses where AI assistance was used in this project, what it produced, and what I reviewed, accepted or changed. Decisions, ratings and test results are mine. AI-drafted text is marked as a draft until I confirm it.

## 2. Tool

Claude Code (Anthropic), working in the local repository under written rules: no real addresses, hostnames, keys or raw scan output in the repository, no invented results, and no commit without my review of the staged changes.

## 3. Usage log

| Date | What the AI drafted or edited | What I reviewed, accepted or changed |
|---|---|---|
| 27th October 2026 | Renamed `gitignore` to `.gitignore` and stopped tracking a local tooling file | Reviewed the staged changes and committed them myself |
| 27th October 2026 | Document 04, D-01: added a third option, a draft recommendation, reasoning and trade-offs | Reviewed the staged changes and approved the commit. The D-01 decision is still open |
| 27th October 2026 | Document 05, section 4: draft expected results for V-01 to V-15 | Reviewed the staged changes and approved the commit. Expected results are still to be confirmed before any test runs |
| 27th October 2026 | Created this document | Reviewed the staged changes and approved the commit |
| 27th October 2026 | Header fixes in documents 02, 04 and 05. Document 01, section 6.3: SMB marked as to be decided. Matrix: Phase 0 test IDs added per threat. Added `evidence/phase0/README.md` | Reviewed the staged changes and approved the commit |
| 27th October 2026 | Added `scripts/phase0-collect.sh` (read-only collection script, not yet run) and `docs/phase0-checklist.md` | Reviewed the staged changes and approved the commit |
| 27th October 2026 | Document 04, D-01: recorded my decision (option 3) and my list of earlier changes, and removed the draft markers from the reasoning | Reviewed the staged changes and approved the commit |
| 27th October 2026 | Document 01: OMV version, baseline account and network state, matching D-01 | Reviewed the staged changes and approved the commit |
| 27th October 2026 | Documents 01 and 04: recorded my answers on the network connection, install option and case software | **[TODO: owner review]** |

## 4. Revision log

| Version | Date | Change | Reason |
|---|---|---|---|
| 0.1 | 27th October 2026 | Document created with first log entries (drafted with AI assistance) | Disclose AI assistance |
| 0.2 | 27th October 2026 | Marked first entries as reviewed and added a log entry for Phase 0 preparation fixes | Keep the log current |
| 0.3 | 27th October 2026 | Added log entry for the Phase 0 script and checklist | Keep the log current |
| 0.4 | 27th October 2026 | Added log entry for recording D-01 | Keep the log current |
| 0.5 | 27th October 2026 | Added log entry for document 01 update | Keep the log current |
| 0.6 | 27th October 2026 | Added log entry for owner answers | Keep the log current |
