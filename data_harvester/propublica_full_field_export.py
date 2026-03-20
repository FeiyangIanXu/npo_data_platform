import argparse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

from propublica_client import build_session, fetch_organization_payload
from propublica_poc_harvester import CSV_FILE_PATH, get_targets_from_csv


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "output" / "propublica"
DEFAULT_WORKERS = 6


def flatten_payload(ein: str, target_company: str, payload: dict) -> list[dict]:
    organization = payload.get("organization", {})
    if not isinstance(organization, dict):
        organization = {}
    filings = payload.get("filings_with_data", [])
    if not isinstance(filings, list):
        filings = []

    base = {
        "ein": ein,
        "target_company": target_company,
        "api_version": payload.get("api_version"),
        "data_source": payload.get("data_source"),
    }
    base.update({f"org_{key}": value for key, value in organization.items()})

    rows = []
    for filing in filings:
        filing_dict = filing if isinstance(filing, dict) else {}
        row = dict(base)
        row.update({f"filing_{key}": value for key, value in filing_dict.items()})
        rows.append(row)
    if rows:
        return rows
    return [base]


def fetch_one(session: requests.Session, row, timeout: int) -> tuple[list[dict], dict]:
    ein = row.ein
    try:
        payload = fetch_organization_payload(session, ein, timeout=timeout)
        rows = flatten_payload(ein, row.company_name, payload)
        return rows, {"ein": ein, "target_company": row.company_name, "status": "ok", "row_count": len(rows), "error": ""}
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else None
        status = "not_found" if status_code == 404 else "error"
        return [], {
            "ein": ein,
            "target_company": row.company_name,
            "status": status,
            "row_count": 0,
            "error": str(exc),
        }
    except (requests.RequestException, ValueError) as exc:
        return [], {
            "ein": ein,
            "target_company": row.company_name,
            "status": "error",
            "row_count": 0,
            "error": str(exc),
        }


def export_all_fields(targets: pd.DataFrame, timeout: int, workers: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    session = build_session()
    all_rows: list[dict] = []
    audit_rows: list[dict] = []
    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        future_map = {executor.submit(fetch_one, session, row, timeout): row for row in targets.itertuples(index=False)}
        for future in as_completed(future_map):
            row = future_map[future]
            rows, audit_row = future.result()
            all_rows.extend(rows)
            audit_rows.append(audit_row)
            logging.info("EIN %s -> %s (%s rows)", row.ein, audit_row["status"], audit_row["row_count"])
    return pd.DataFrame(all_rows), pd.DataFrame(audit_rows).sort_values(by=["status", "ein"]).reset_index(drop=True)


def save_outputs(full_df: pd.DataFrame, audit_df: pd.DataFrame) -> tuple[Path, Path, Path]:
    date_tag = datetime.now().strftime("%Y%m%d")
    csv_path = OUTPUT_DIR / f"propublica_all_fields_{date_tag}.csv"
    xlsx_path = OUTPUT_DIR / f"propublica_all_fields_{date_tag}.xlsx"
    audit_path = OUTPUT_DIR / f"propublica_all_fields_audit_{date_tag}.csv"
    full_df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    try:
        full_df.to_excel(xlsx_path, index=False)
    except Exception:
        time_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
        xlsx_path = OUTPUT_DIR / f"propublica_all_fields_{time_tag}.xlsx"
        full_df.to_excel(xlsx_path, index=False)
    audit_df.to_csv(audit_path, index=False, encoding="utf-8-sig")
    return csv_path, xlsx_path, audit_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Export flattened ProPublica organization + filing fields.")
    parser.add_argument("--sample-size", type=int, default=10, help="How many target EINs to check. 0 means all.")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout seconds.")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS, help="Concurrent workers.")
    args = parser.parse_args()

    targets = get_targets_from_csv(CSV_FILE_PATH)
    if args.sample_size and args.sample_size > 0:
        targets = targets.head(args.sample_size).copy()

    full_df, audit_df = export_all_fields(targets, timeout=args.timeout, workers=args.workers)
    csv_path, xlsx_path, audit_path = save_outputs(full_df, audit_df)

    print("====== ProPublica All-Field Export ======")
    print(f"Checked EINs: {len(targets)}")
    print(f"Rows exported: {len(full_df)}")
    print(f"Columns exported: {len(full_df.columns)}")
    print(f"Saved CSV: {csv_path}")
    print(f"Saved XLSX: {xlsx_path}")
    print(f"Saved audit CSV: {audit_path}")


if __name__ == "__main__":
    main()
