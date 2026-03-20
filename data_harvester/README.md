# Data Harvester

This folder contains the data-source research, harvesting scripts, comparison tools, and generated outputs used for nonprofit data collection work.

## Current Layout

- `bulk_data_harvester.py`
  GT / GiveTuesday historical batch export.
- `compare_target_with_api.py`
  GT coverage check against the target EIN list.
- `more_request.py`
  GT endpoint snapshot tool.
- `propublica_client.py`
  Low-level ProPublica API client.
- `propublica_mapper.py`
  ProPublica normalization logic.
- `propublica_poc_harvester.py`
  Main ProPublica POC batch harvester.
- `propublica_latest_snapshot.py`
  Latest-filing snapshot builder.
- `propublica_to_backend_snapshot.py`
  Backend-friendly ProPublica snapshot export.
- `propublica_full_field_export.py`
  Full flattened ProPublica export.
- `propublica_yearly_filings_export.py`
  Yearly filing-oriented full export.
- `compare_gt_vs_propublica.py`
  Freshness comparison: GT vs ProPublica.
- `compare_propublica_with_first100.py`
  Comparison against the original manual Excel benchmark.
- `compare_propublica_with_nonprofits_csv.py`
  Comparison against the cleaned CSV benchmark.

## Subfolders

- `docs/`
  Markdown reports and design notes.
- `input/`
  Input copies or generated working inputs.
- `output/`
  Generated exports, reports, review lists, and audits.
  Current subfolders:
  `output/gt/`
  `output/gt/snapshots/`
  `output/gt/reports/`
  `output/propublica/`
  `output/propublica/reports/`
- `reference/`
  Reference files such as the GT dictionary and ProPublica field map.
- `legacy/`
  Older prototype or one-off scripts kept for reference only.

## Recommended Starting Points

- GT coverage work:
  `compare_target_with_api.py`
  `bulk_data_harvester.py`
- ProPublica work:
  `propublica_poc_harvester.py`
  `propublica_latest_snapshot.py`
  `compare_propublica_with_nonprofits_csv.py`

## Notes

- The `legacy/` folder is not part of the main current workflow.
- GT scripts now write to `output/gt/`.
- GT endpoint snapshots write to `output/gt/snapshots/`.
- ProPublica scripts now write to `output/propublica/`.
- ProPublica comparison reports write to `output/propublica/reports/`.
- The active benchmark for machine comparison is `backend/data/nonprofits_100.csv`.
