# CLAUDE.md – NAS-Hardening-project

This file gives Claude Code the rules for working in this repository. It is local only and is listed in `.gitignore`. Do not commit it.

## Project summary

A documented, evidence-based hardening project for a home NAS (Raspberry Pi 5, OpenMediaVault, SSD) that replaces third-party cloud storage. The repository is **public** and is part of the owner's portfolio, so what is published matters.

Owner: William Drummond. The owner makes all decisions. Claude Code proposes and drafts.

Document set (adjust if the layout differs **[TODO: confirm paths]**):

- `README.md` – overview, status, progress
- `docs/01-scope-and-assets.md` – scope, assets, data flows, trust boundaries, phases
- `docs/02-threat-analysis.md` – threats T-01 to T-21, ratings, Tailscale trust analysis, treatment plan
- `docs/04-design-decisions.md` – decision records (D-xx)
- `docs/05-verification.md` – test plan, findings, log, stage checks
- `docs/ai-usage.md` – disclosure of AI assistance
- `requirements-matrix.csv` – threat to requirement to control to test traceability
- `evidence/` – sanitised evidence only

## Hard rules: what must never be written to the repository

Never write, paste, suggest or commit any of the following, in any file, commit message or diff:

- Real IP addresses (LAN or public), hostnames, usernames, MAC addresses, Wi-Fi network names or passwords
- Keys, tokens, passwords, auth keys, backup repository details
- Any port number the owner **chose** (for example the WireGuard port). Use a placeholder such as `<WG-PORT>`. Standard ports (22, 80, 445) are fine
- Exact patch-level software versions from baseline scans that show unfixed vulnerabilities. Use the major version, or leave it out until the finding is fixed
- Raw scan output, unreviewed screenshots, or anything copied from the raw evidence location

Use placeholders: `192.0.2.x` for addresses, `nas.example` for hostnames, `<NAS-IP>`, `<USER>` and similar for the rest.

If the owner pastes raw output into the conversation, sanitise it before using any of it, and never write the raw version to a file inside the repository.

Do not read, open or list files outside this repository, and do not ask for the raw evidence folder.

## Git rules

- Work on a branch, not on `main`
- Stage named files only. Never run `git add -A` or `git add .`
- Never use `git add -f`
- Show `git diff --staged` and wait for the owner's approval before every commit
- **Do not push.** The owner pushes after reviewing
- Never force push, rewrite history, or amend published commits
- Commit messages are short and factual, for example `Phase 0: add V-01 TCP scan result (sanitised)`
- Before finishing any task, check staged changes for leaked details, for example:
  - `git diff --staged | grep -nE '([0-9]{1,3}\.){3}[0-9]{1,3}'`
  - `git diff --staged | grep -niE '([0-9a-f]{2}:){5}[0-9a-f]{2}'`
  - `git diff --staged | grep -niE 'password|passwd|secret|token|private key'`

  Report every match. Do not decide on your own that a match is harmless.

## Honesty and evidence rules

- Never invent test results, scan output, findings, versions, dates or evidence. If something is not known, write `[TODO]`
- Do not mark a test as pass or fail unless the owner has supplied the actual result
- Phase 0 is observation only. Do not describe baseline findings as fixed, and do not describe planned work as done
- Ratings in document 02 and decisions in document 04 are the owner's. Propose changes and explain the reason, but do not finalise them
- Do not claim ISO compliance or certification. The method is a simplified risk assessment structured after ISO/IEC 27005, with controls cross-referenced to ISO/IEC 27002:2022 themes. ISO/SAE 21434 is an automotive standard and may be mentioned only as an analogy
- Do not write that testing "proves" security. Use wording such as "verified that the control held against the test, with evidence"
- Do not state clause-level ISO mappings unless the owner confirms them against the standard text

## Document conventions

- UK English, plain factual tone, no marketing language
- Keep the existing style: status header block, numbered sections, ID tables, `[TODO]` markers, revision log at the end
- Identifiers: threats `T-xx`, requirements `SR-xx`, tests `V-xx`, findings `FND-xx`, decisions `D-xx`, assets `A-xx`, objectives `O-x`, flows `F-x`
- Never reuse or renumber an existing ID. Add new IDs at the end
- When a document changes, update its "Last updated" date and add a revision log row
- When an ID or mapping changes in one document, check the related documents (01, 02, 04, 05 and the matrix) and report any inconsistency instead of silently editing several files
- Keep cross-references to files that do not exist yet as plain text, not links

## AI disclosure

After any session that changes the repository, offer a short dated entry for `docs/ai-usage.md` saying what was drafted or edited and what the owner reviewed, accepted or changed. The owner decides what is published.

## Working style

- Make small, specific changes, and explain each one in a line or two
- Ask before making any change that touches several documents
- If a request would break a hard rule above, say so and stop. Do not work around it
