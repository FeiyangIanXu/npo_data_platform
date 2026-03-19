import argparse
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

from propublica_client import build_session, fetch_organization_payload
from propublica_mapper import CANONICAL_COLUMNS, payload_to_canonical_rows, summarize_payload


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

SCRIPT_DIR = Path(__file__).resolve().parent
CSV_FILE_PATH = SCRIPT_DIR.parent / "backend" / "data" / "nonprofits_100.csv"
OUTPUT_DIR = SCRIPT_DIR / "output"
DEFAULT_WORKERS = 6


def normalize_ein(value) -> str:
    if pd.isna(value):
        return ""
    digits = re.sub(r"\D", "", str(value))
    if not digits:
        return ""
    if len(digits) > 9:
        digits = digits[-9:]
    return digits.zfill(9)


def get_targets_from_csv(file_path: Path) -> pd.DataFrame:
    df = pd.read_csv(file_path, skiprows=5, header=None)
    targets = pd.DataFrame(
        {
            "company_name": df.iloc[:, 2].astype(str).str.strip(),
            "ein": df.iloc[:, 8].map(normalize_ein),
        }
    )
    targets = targets[(targets["company_name"] != "") & (targets["ein"] != "")]
    targets = targets.drop_duplicates(subset=["ein"], keep="first").reset_index(drop=True)
    return targets


def fetch_one(session: requests.Session, row, timeout: int) -> tuple[list[dict], dict]:
    ein = row.ein
    try:
        payload = fetch_organization_payload(session, ein, timeout=timeout)
        filing_rows = payload_to_canonical_rows(ein, payload)
        summary = summarize_payload(ein, payload)
        summary.update(
            {
                "target_company": row.company_name,
                "status": "ok" if summary["filing_count"] > 0 else "empty",
                "error": "",
            }
        )
        return filing_rows, summary
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else None
        status = "not_found" if status_code == 404 else "error"
        summary = {
            "ein": ein,
            "target_company": row.company_name,
            "status": status,
            "error": str(exc),
            "filing_count": 0,
            "latest_tax_year": None,
            "latest_form_type": "",
            "has_2024_plus": False,
            "has_2025_plus": False,
        }
        return [], summary
    except (requests.RequestException, ValueError) as exc:
        summary = {
            "ein": ein,
            "target_company": row.company_name,
            "status": "error",
            "error": str(exc),
            "filing_count": 0,
            "latest_tax_year": None,
            "latest_form_type": "",
            "has_2024_plus": False,
            "has_2025_plus": False,
        }
        return [], summary


def fetch_all_targets(targets: pd.DataFrame, timeout: int, workers: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    session = build_session()
    all_rows: list[dict] = []
    audit_rows: list[dict] = []

    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        future_map = {
            executor.submit(fetch_one, session, row, timeout): row for row in targets.itertuples(index=False)
        }
        for future in as_completed(future_map):
            row = future_map[future]
            filing_rows, audit_row = future.result()
            all_rows.extend(filing_rows)
            audit_rows.append(audit_row)
            logging.info(
                "EIN %s -> %s (%s filings, latest=%s)",
                row.ein,
                audit_row["status"],
                audit_row["filing_count"],
                audit_row["latest_tax_year"],
            )

    filings_df = pd.DataFrame(all_rows)
    if filings_df.empty:
        filings_df = pd.DataFrame(columns=CANONICAL_COLUMNS)
    else:
        for column in CANONICAL_COLUMNS:
            if column not in filings_df.columns:
                filings_df[column] = None
        filings_df = filings_df[CANONICAL_COLUMNS].sort_values(
            by=["ein", "tax_year", "filing_date"], ascending=[True, False, False]
        )

    audit_df = pd.DataFrame(audit_rows).sort_values(by=["status", "ein"]).reset_index(drop=True)
    return filings_df, audit_df


def export_outputs(filings_df: pd.DataFrame, audit_df: pd.DataFrame) -> tuple[Path, Path, Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    date_tag = datetime.now().strftime("%Y%m%d")
    filings_xlsx_path = OUTPUT_DIR / f"propublica_filings_{date_tag}.xlsx"
    filings_csv_path = OUTPUT_DIR / f"propublica_filings_{date_tag}.csv"
    audit_path = OUTPUT_DIR / f"propublica_audit_{date_tag}.csv"
    try:
        filings_df.to_excel(filings_xlsx_path, index=False)
    except PermissionError:
        time_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
        filings_xlsx_path = OUTPUT_DIR / f"propublica_filings_{time_tag}.xlsx"
        filings_df.to_excel(filings_xlsx_path, index=False)
    filings_df.to_csv(filings_csv_path, index=False, encoding="utf-8-sig")
    audit_df.to_csv(audit_path, index=False, encoding="utf-8-sig")
    return filings_xlsx_path, filings_csv_path, audit_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Harvest ProPublica nonprofit filing data for target EINs.")
    parser.add_argument("--sample-size", type=int, default=10, help="How many target EINs to check. 0 means all.")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout seconds.")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS, help="Concurrent workers.")
    args = parser.parse_args()

    targets = get_targets_from_csv(CSV_FILE_PATH)
    if targets.empty:
        raise SystemExit("No valid EINs found in target CSV.")

    if args.sample_size and args.sample_size > 0:
        targets = targets.head(args.sample_size).copy()

    filings_df, audit_df = fetch_all_targets(targets, timeout=args.timeout, workers=args.workers)
    filings_xlsx_path, filings_csv_path, audit_path = export_outputs(filings_df, audit_df)

    ok_count = int((audit_df["status"] == "ok").sum()) if not audit_df.empty else 0
    newer_2024 = int(audit_df["has_2024_plus"].sum()) if not audit_df.empty else 0
    newer_2025 = int(audit_df["has_2025_plus"].sum()) if not audit_df.empty else 0

    print("====== ProPublica POC Harvest ======")
    print(f"Checked EINs: {len(targets)}")
    print(f"Successful EINs: {ok_count}")
    print(f"Rows exported: {len(filings_df)}")
    print(f"EINs with 2024+: {newer_2024}")
    print(f"EINs with 2025+: {newer_2025}")
    print(f"Saved filings XLSX: {filings_xlsx_path}")
    print(f"Saved filings CSV: {filings_csv_path}")
    print(f"Saved audit CSV: {audit_path}")


if __name__ == "__main__":
    main()
