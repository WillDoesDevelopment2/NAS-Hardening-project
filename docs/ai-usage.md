# AI Usage

> **Status:** Draft v0.13 · Last updated: 28th October 2026
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
| 27th October 2026 | Documents 01 and 04: recorded my answers on the network connection, install option and case software | Reviewed the staged changes and approved the commits |
| 27th October 2026 | Document 05, section 4: expected results updated to match D-01, V-13 reworded, draft markers removed. Matrix: draft wording removed | I confirmed the expected results and the V-13 answer, then reviewed the staged changes and approved the commit |
| 27th October 2026 | Document 01, section 10: recorded my answers on the assumptions and reworded the network compromise assumption as I asked | Reviewed the staged changes and approved the commit |
| 27th October 2026 | Document 02: T-08, T-11, T-03 and section 9 updated after the document 01 assumptions were confirmed. Document 01: CGNAT note | Reviewed the staged changes and approved the commit |
| 27th October 2026 | Added `scripts/sanitise.py`, a script that replaces addresses, MAC addresses, keys, serial numbers and mapped values in raw evidence. Tested on made-up data only | Reviewed the changes and approved the commit |
| 27th October 2026 | Document 02, section 7: checked each Tailscale statement against the Tailscale documentation while I was away, added corrections and sources | Reviewed the changes and approved the commit |
| 28th October 2026 | Walked me through the SD card hash checks. Recorded the image date and hash I supplied in documents 04 and 05 and ticked the completed prerequisites | I ran the checks, supplied the date and hash, and approved the commit |
| 28th October 2026 | Document 05: recorded the V-13 result I supplied, drafted FND-01 and the log rows, and added a note on what Pass or fail means. Ticked the remaining prerequisites | I ran V-13, supplied the result, chose Fail, changed the password, re-tested, kept the T-01 rating and reviewed the staged changes |
| 28th October 2026 | The collection script I had drafted set the permissions of the NAS root folder to 700 when given `/` as its output folder, which locked the system for non-root users. Gave recovery steps, fixed the script so it only creates a new folder in the home folder or `/tmp` and hands the output back to me, updated the checklist and logged the deviation in document 05 | I recovered the NAS, reported the results and approved the commit |

## 4. Revision log

| Version | Date | Change | Reason |
|---|---|---|---|
| 0.1 | 27th October 2026 | Document created with first log entries (drafted with AI assistance) | Disclose AI assistance |
| 0.2 | 27th October 2026 | Marked first entries as reviewed and added a log entry for Phase 0 preparation fixes | Keep the log current |
| 0.3 | 27th October 2026 | Added log entry for the Phase 0 script and checklist | Keep the log current |
| 0.4 | 27th October 2026 | Added log entry for recording D-01 | Keep the log current |
| 0.5 | 27th October 2026 | Added log entry for document 01 update | Keep the log current |
| 0.6 | 27th October 2026 | Added log entry for owner answers | Keep the log current |
| 0.7 | 27th October 2026 | Added log entry for expected results update | Keep the log current |
| 0.8 | 27th October 2026 | Added log entry for document 01 assumptions | Keep the log current |
| 0.9 | 27th October 2026 | Added log entry for document 02 updates | Keep the log current |
| 0.10 | 28th October 2026 | Added log entries for the sanitise script and the Tailscale check | Keep the log current |
| 0.11 | 28th October 2026 | Added log entry for the SD card image record | Keep the log current |
| 0.12 | 28th October 2026 | Added log entry for the V-13 result | Keep the log current |
| 0.13 | 28th October 2026 | Added log entry for the collection script defect and fix | Keep the log current |
