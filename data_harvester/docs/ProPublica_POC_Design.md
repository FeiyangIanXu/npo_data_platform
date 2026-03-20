# ProPublica API POC Design

## Goal

Validate whether the ProPublica Nonprofit Explorer API can provide fresher organization filing data than the current GTDC `990basic120fields` workflow.

This phase is a POC only.

We will:

- keep the current GTDC pipeline intact
- add a separate ProPublica harvesting path
- compare freshness, coverage, and field usability
- defer any production merge until the POC passes

## Why This POC Exists

The current GTDC harvest flow in `bulk_data_harvester.py` is stable, but its returned filing years are often too old.

Observed problem:

- many records stop at tax year `2023`
- some organizations are still effectively only useful through `2022`
- for late March 2026, we expect many organizations to have at least `2024` filings available
- some organizations may already expose `2025` data depending on filing timing

The POC is meant to answer one question clearly:

Can ProPublica materially improve year freshness enough to justify deeper integration work?

## What "Mapper" Means

A `mapper` is a translation or normalization layer between two schemas.

In this project:

- source schema = fields returned by ProPublica
- target schema = the fields we want the project to use downstream

Important clarification for phase 1:

- the existing 164-field schema is not treated as fixed
- those field names were originally useful for making the spreadsheet machine-readable
- they are not automatically the right target schema for a new source
- phase 1 should avoid forcing ProPublica into that old structure unless there is a clear payoff

Example:

- ProPublica may return a field like `total_revenue`
- the current project may expect something like `part_i_summary_12_total_revenue_cy`

The mapper or normalization layer decides:

- which source field populates which target field
- how values are cleaned or converted
- what happens when a field is missing
- which source wins if GTDC and ProPublica both provide a value

Without a normalization layer, we only have raw API data.
With one, we can turn raw source data into project-usable data.

## POC Scope

This first phase should stay narrow.

Included:

- organization-level pull from ProPublica by EIN
- extraction of filing-year level records
- identification of latest filing year per EIN
- normalization of a small set of high-value financial fields
- comparison against current GTDC latest-year coverage
- export of audit files for manual review

Not included:

- replacing GTDC
- rewriting the backend database pipeline
- full legacy-schema compatibility
- frontend changes
- XML parsing fallback

## Proposed New Files

The POC should add these files under `data_harvester/`.

### 1. `propublica_client.py`

Purpose:

- low-level HTTP client for ProPublica API
- request organization JSON by EIN
- normalize transport-level errors

Responsibilities:

- build requests session
- fetch `/api/v2/organizations/{ein}.json`
- return parsed JSON payload
- expose small helper functions for safe field access

### 2. `propublica_mapper.py`

Purpose:

- convert ProPublica raw organization payload into normalized filing rows

Responsibilities:

- extract `filings_with_data`
- flatten filing summaries into row-per-filing format
- populate a small canonical schema for comparison
- keep raw source keys if useful for debugging

This file is where the normalization logic lives.

### 3. `propublica_poc_harvester.py`

Purpose:

- batch-run the POC for the target EIN list

Responsibilities:

- load target EINs from `backend/data/nonprofits_100.csv`
- call `propublica_client.py`
- apply `propublica_mapper.py`
- export combined row dataset and audit dataset

### 4. `compare_gt_vs_propublica.py`

Purpose:

- compare freshness and coverage between GTDC and ProPublica

Responsibilities:

- compute latest year by EIN from GT output
- compute latest year by EIN from ProPublica output
- flag where ProPublica is newer
- flag where ProPublica is missing
- summarize uplift

### 5. `reference/propublica_field_mapping.csv`

Purpose:

- store lightweight field-normalization rules outside Python code

Recommended columns:

- `target_field`
- `propublica_field_path`
- `transform_rule`
- `priority`
- `notes`

This should remain small in phase 1.
It documents canonical field choices, not a recreation of the full legacy schema.

## Normalization Layer Design

The normalization layer should be small and explicit in phase 1.

### Phase 1 Canonical Output Schema

Each ProPublica filing row should export at least these canonical columns:

- `source`
- `ein`
- `organization_name`
- `tax_year`
- `filing_date`
- `tax_prd`
- `form_type`
- `total_revenue`
- `total_expenses`
- `total_assets`
- `net_assets`
- `employee_count`
- `is_latest_filing_for_ein`
- `raw_available`

Recommended fixed value:

- `source = "propublica"`

### Why A Canonical Schema First

We should not try to force ProPublica into the old 164-field structure immediately.

First build a small canonical comparison layer:

- enough to evaluate freshness
- enough to evaluate core financial usability
- enough to decide whether full integration is worth doing

If phase 1 succeeds, then we decide among three follow-up directions:

- keep using the canonical schema for the new source
- expand the canonical schema gradually
- add selective compatibility mappings only where the backend truly needs them

This is intentionally different from assuming:

- `ProPublica -> legacy 164-field schema`

That assumption would create unnecessary complexity too early.

### Normalization Strategy

Use 3 tiers:

1. direct mapping
2. transformed mapping
3. unsupported field

Examples:

- direct mapping: source field copies directly
- transformed mapping: source needs renaming, parsing, or numeric cleaning
- unsupported field: field has no reliable ProPublica equivalent yet

The default rule in phase 1 should be:

- if a field is not clearly useful for freshness or core financial comparison, do not normalize it yet

### Output Rule

The normalization layer should return:

- one row per filing year
- normalized numeric columns where possible
- raw strings preserved if parsing fails
- enough metadata to trace where the value came from
- clean canonical names that are understandable without the old spreadsheet context

## Output Design

The POC should write outputs into `data_harvester/output/`.

### 1. ProPublica Filing Rows

File:

- `propublica_filings_<date>.xlsx`
- optional CSV mirror: `propublica_filings_<date>.csv`

Contents:

- one row per EIN per filing year
- clean canonical comparison columns

### 2. ProPublica Audit

File:

- `propublica_audit_<date>.csv`

Contents:

- `ein`
- `target_company`
- `status`
- `error`
- `filing_count`
- `latest_tax_year`
- `latest_form_type`
- `has_2024_plus`
- `has_2025_plus`

### 3. GT vs ProPublica Freshness Comparison

File:

- `gt_vs_propublica_freshness_<date>.csv`

Contents:

- `ein`
- `target_company`
- `gt_latest_tax_year`
- `propublica_latest_tax_year`
- `year_delta`
- `propublica_newer`
- `gt_missing`
- `propublica_missing`
- `comparison_status`

### 4. Summary Markdown

File:

- `ProPublica_POC_Report_<date>.md`

Contents:

- total EINs checked
- successful fetch count
- ProPublica latest year distribution
- how many EINs improved beyond GT
- sample mismatches
- recommendation for next step

## How It Coexists With `bulk_data_harvester.py`

The POC should coexist, not replace.

### Current GTDC Script Remains

`bulk_data_harvester.py` should remain unchanged in phase 1.

It continues to provide:

- current GTDC batch pull
- current GT audit outputs
- current dictionary-based column renaming

### New ProPublica Path Is Parallel

The new ProPublica files should not import GT-specific field dictionary logic.

Instead:

- GTDC flow stays GTDC-specific
- ProPublica flow stays ProPublica-specific
- comparison happens in a separate script

This separation avoids accidental breakage.

### Future Merge Path

If the POC passes, the next phase would add a shared abstraction such as:

- `source adapters`
- `shared target loader`
- `shared canonical record schema`
- `merge policy by EIN + tax_year`

But that should wait until we see real POC results.

## Phase 1 Execution Plan

### Step 1. Build ProPublica client

Deliverable:

- fetch one EIN successfully
- save one raw sample for inspection if needed

### Step 2. Build normalization layer

Deliverable:

- flatten one organization payload into filing rows
- identify latest filing year correctly

### Step 3. Batch-run target EINs

Deliverable:

- harvest target list
- export filing dataset and audit file

### Step 4. Compare against GTDC

Deliverable:

- per-EIN latest-year comparison
- aggregate freshness uplift summary

### Step 5. Document findings

Deliverable:

- markdown POC report
- recommendation for integrate / reject / partial use

## Phase 1 Acceptance Criteria

The POC is successful if most of these conditions are met.

### Must Have

- ProPublica API can be fetched reliably for the target EIN list
- `filings_with_data` can be extracted into row-level records
- latest filing year can be determined per EIN
- outputs are reproducible and easy to audit
- no changes are required to existing GTDC scripts

### Strong Success Signals

- a meaningful share of target EINs show `2024` data
- some EINs show newer data than GTDC
- core financial fields map cleanly for most returned filings
- missing or malformed cases are understandable rather than random

### Fail Conditions

The POC should be considered weak or failed if:

- API response coverage is poor for the target EINs
- filing rows are too sparse to support even a small canonical schema
- latest year is not consistently newer than GT
- the normalization burden appears disproportionate to the freshness gain

## Risks

### 1. Schema mismatch risk

ProPublica is not GTDC.
Its field names and semantics will not line up automatically with the old schema.

### 2. Partial coverage risk

Some EINs may exist in GTDC but not return usable `filings_with_data` from ProPublica.

### 3. Field completeness risk

Freshness may improve while field completeness decreases.

### 4. Name mismatch risk

Organization naming may differ across sources even when EIN matches.

### 5. Form-type variation risk

Some organizations may file variants that make certain fields unavailable or non-comparable.

## Recommendation For Implementation

Phase 1 should optimize for evidence, not elegance.

That means:

- small number of new files
- clean separation from GTDC code
- explicit normalization logic
- audit-heavy outputs
- no production merge yet

## Immediate Next Build

After this design is approved, the next implementation steps should be:

1. create `propublica_client.py`
2. create `propublica_mapper.py`
3. create `propublica_poc_harvester.py`
4. run a small sample first
5. inspect output before running all target EINs
