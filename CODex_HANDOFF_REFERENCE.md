# Codex Handoff Reference (Project Context + Plan)

> Purpose: This file is a persistent handoff for future Codex sessions (especially local IDE Codex), summarizing decisions, current status, and the next execution plan.

## 1) Collaboration mode decision (important)

We agreed to use **Mode A: GitHub as the single source of truth**.

- Work should be developed on feature branches.
- Changes are pushed to GitHub and merged via PR.
- Local machine sync uses `git fetch` / `git pull`.
- Final version truth lives on GitHub, not in temporary container state.

## 2) Git concepts clarified in prior discussion

- `origin` is the alias for remote repository URL.
- `fetch` downloads remote refs/metadata and does **not** change working files.
- `pull` = `fetch + merge/rebase` and can change local branch files.
- Branch and PR are separate concepts from fetch/pull:
  - Branch = development line.
  - PR = review + merge workflow.

## 3) Baseline freeze milestone completed

A baseline tag has been created and pushed:

- Tag name: `baseline-old-csv-mvp`
- Meaning: old CSV-based MVP runnable baseline is frozen.

This gives a safe rollback point before GiveTuesday API migration.

## 4) Sensitive data policy (strict)

We explicitly do **not** want proprietary/raw private data pushed to public remote.

Already aligned with repository intent:

- `README.md` states source proprietary data and generated DB are not included.
- `.gitignore` already includes proprietary data paths under `backend/data/...` and DB artifacts.

Additional local ignore protections were discussed/validated:

- `data_harvester/output/`
- `backend/npo_api_data.db`
- `form-990-xml-parser/`

## 5) Current product direction

We decided to **move toward GiveTuesday API as final data source**.

Main development objective:

1. Batch pull 200+ EIN from GiveTuesday API.
2. Write into new SQLite tables (raw + curated design preferred).
3. Produce comparison report:
   - coverage rate
   - year distribution
   - missingness/null-rate by key fields

## 6) Why this order

Before fully fixing legacy query behavior, we prioritize data-source migration because:

- Current query logic is strongly coupled to old CSV schema.
- If we fix query first and then replace schema, we likely rework twice.
- Better flow: stabilize new schema -> adapt backend query -> adapt frontend.

## 7) Sprint plan (first 90 minutes)

### Goal
Create a minimal repeatable ingestion scaffold (small scope, testable).

### Done criteria

- Feature branch exists: `feature/givetuesday-ingestion-v1`.
- EIN input file exists (small test set first).
- A minimal batch script runs with `--limit` and outputs summary metrics.
- No sensitive outputs are committed.

### Suggested deliverables

- `data_harvester/input/eins_master.csv` (column: `ein`)
- `data_harvester/bulk_givetuesday_ingest.py`
- Local output file (ignored): `data_harvester/output/batch_raw_preview.json`

## 8) Command checklist for next Codex session

### Safety + sync

```bash
git fetch --all --tags
git status
git branch -vv
```

### Branch setup

```bash
git switch main
git pull --ff-only origin main
git switch -c feature/givetuesday-ingestion-v1
```

### Validate ignore behavior

```bash
git check-ignore -v data_harvester/output/test.xlsx
git check-ignore -v backend/npo_api_data.db
git check-ignore -v form-990-xml-parser/.git
```

### Commit minimal scaffold only

```bash
git add data_harvester/input/eins_master.csv data_harvester/bulk_givetuesday_ingest.py .gitignore
git commit -m "feat(data-harvester): add initial GT bulk ingestion scaffold"
git push -u origin feature/givetuesday-ingestion-v1
```

## 9) Immediate next engineering tasks

1. Implement `bulk_givetuesday_ingest.py` with:
   - retry
   - timeout
   - per-EIN status log
   - summary counters
2. Normalize API response shape (list vs nested body differences discovered historically).
3. Store raw records first; avoid over-transforming in first iteration.
4. Add SQLite writer step (`raw_gt_filings` table).
5. Generate first comparison report script (coverage/year/missingness).

## 10) Notes about previous confusion

A prior output containing:

> "Successfully connected to the GivingTuesday API..."

was from a **historic commit message display** (`git show` pager), not a live API request in that moment.

---

If you are a future Codex instance reading this file: continue from Section 7 and execute the first sprint with minimal surface area and strict no-sensitive-data commit discipline.
