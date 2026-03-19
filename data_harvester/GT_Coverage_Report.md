# GT Coverage Report

## Scope

This report summarizes the current GiveTuesday API coverage against the target list in `backend/data/nonprofits_100.csv`.

The work in this folder now uses three main scripts:

- `data_harvester/compare_target_with_api.py`: target-vs-API coverage check by EIN and company name.
- `data_harvester/bulk_data_harvester.py`: batch export of all historical `990basic120fields` records for the target EIN list.
- `data_harvester/more_request.py`: snapshot export for several non-`990basic120fields` endpoints.

## Data Sources

- Target list: `backend/data/nonprofits_100.csv`
- Human-readable target field names: `backend/data/First100.xlsx` row 4
- GT bulk export: `data_harvester/output/all_nonprofits_data_20260319.xlsx`
- GT bulk audit: `data_harvester/output/bulk_harvest_audit_20260319.csv`
- API comparison detail: `data_harvester/output/api_target_comparison.csv`
- Coverage audit detail: `data_harvester/output/coverage_audit_20260223.xlsx`

## Coverage Summary

Target population is measured from `nonprofits_100.csv` after EIN normalization and deduplication.

- Target unique EINs: 97
- API ok: 94
- API empty: 3
- API error: 0
- EIN coverage: 94 / 97 = 96.91%
- EIN + company-name match: 78 / 97 = 80.41%
- Rows exported in the GT bulk historical dataset: 1154

The three target EINs currently returning empty results are:

- `059347233` - The Glenridge on Palmer Ranch, Inc.
- `133102941` - Toby & Leon Cooperman Sinai Residences of Boca Raton (Filed with 990-PF)
- `463093940` - The Osborn (Filed with 990 EZ)

## What The Bulk Export Contains

`all_nonprofits_data_20260319.xlsx` is not a dump of the entire GiveTuesday database.

It contains:

- All historical rows returned by the `irs-data/990basic120fields` endpoint
- Only for EINs found in the target file
- Only for target EINs where the API returned records

It does not contain:

- Organizations outside the target EIN list
- Rows from other GT endpoints such as `revoked`, `postcard`, or `pub78-deductible`
- Records for the three target EINs that currently return empty API results

## Endpoint Snapshot Files

`more_request.py` exports small endpoint samples into `data_harvester/output/`:

- `bmf_530196605.xlsx`
- `efilexml_842929872.xlsx`
- `postcard_000100514.xlsx`
- `pub78-deductible_000635913.xlsx`
- `revoked_000065837.xlsx`

These files are useful for endpoint exploration and schema inspection, but they are not the main coverage dataset for the target retirement-company analysis.

## Field Extraction Outputs

The following files were generated to support field gap analysis:

- `data_harvester/output/fields_nonprofits_100_csv.txt`
- `data_harvester/output/fields_nonprofits_100_csv.md`
- `data_harvester/output/fields_all_nonprofits_data_20260223_xlsx.txt`
- `data_harvester/output/fields_all_nonprofits_data_20260223_xlsx.md`
- `data_harvester/output/fields_first100_row4_human.txt`
- `data_harvester/output/field_comparison_nonprofits_vs_gt.md`

Use `fields_first100_row4_human.txt` for a more human-readable view of the target fields, and compare it against the GT export field lists.

## Current Recommendation

For ongoing work:

- Use `compare_target_with_api.py` for coverage analysis and audit.
- Use `bulk_data_harvester.py` for batch historical export.
- Keep `more_request.py` only as an endpoint snapshot tool.

This is a better structure than the earlier ad hoc scripts because it now has:

- stable proxy handling
- consistent `body.results` parsing
- deterministic audit outputs
- reduced Windows encoding failure risk
