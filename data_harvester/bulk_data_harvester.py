import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BASE_URL = "https://990-infrastructure.gtdata.org/"
API_ENDPOINT = "irs-data/990basic120fields"
SCRIPT_DIR = Path(__file__).resolve().parent
CSV_FILE_PATH = SCRIPT_DIR.parent / "backend" / "data" / "nonprofits_100.csv"
DICTIONARY_FILE_PATH = SCRIPT_DIR / "reference" / "GTDC 990 API - Data Dictionary.xlsx"
OUTPUT_DIR = SCRIPT_DIR / "output"
SHEET_NAME = "990 Basic 120 Fields "
DEFAULT_WORKERS = 8


def normalize_ein(value) -> str:
    if pd.isna(value):
        return ""
    digits = re.sub(r"\D", "", str(value))
    if not digits:
        return ""
    if len(digits) > 9:
        digits = digits[-9:]
    return digits.zfill(9)


def build_session() -> requests.Session:
    session = requests.Session()
    session.trust_env = False
    return session


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
    logging.info("Loaded %s unique EINs from %s.", len(targets), file_path)
    return targets


def load_column_mapping(file_path: Path, sheet_name: str) -> dict:
    logging.info("Loading data dictionary from %s [%s]...", file_path, sheet_name)
    df_dict = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        usecols=["Variable Name", "Variable Location & Description"],
    ).fillna("")
    mapping = dict(zip(df_dict["Variable Name"], df_dict["Variable Location & Description"]))
    logging.info("Loaded %s dictionary entries.", len(mapping))
    return mapping


def extract_results(payload: dict) -> list:
    if not isinstance(payload, dict):
        return []
    body = payload.get("body", {})
    if not isinstance(body, dict):
        return []
    results = body.get("results", [])
    return results if isinstance(results, list) else []


def fetch_all_data_for_ein(session: requests.Session, ein: str) -> tuple[str, list, str]:
    try:
        response = session.get(BASE_URL + API_ENDPOINT, params={"ein": ein}, timeout=30)
        response.raise_for_status()
        results = extract_results(response.json())
        return ein, results, ""
    except requests.exceptions.RequestException as exc:
        logging.error("Request failed for EIN %s: %s", ein, exc)
        return ein, [], str(exc)
    except ValueError as exc:
        logging.error("Invalid JSON for EIN %s: %s", ein, exc)
        return ein, [], str(exc)


def fetch_all_targets(targets: pd.DataFrame, workers: int) -> tuple[list, pd.DataFrame]:
    session = build_session()
    all_records = []
    audit_rows = []

    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        future_map = {
            executor.submit(fetch_all_data_for_ein, session, row.ein): row
            for row in targets.itertuples(index=False)
        }
        for future in as_completed(future_map):
            row = future_map[future]
            ein, records, error = future.result()
            status = "ok" if records else ("error" if error else "empty")
            all_records.extend(records)
            audit_rows.append(
                {
                    "ein": ein,
                    "target_company": row.company_name,
                    "status": status,
                    "record_count": len(records),
                    "error": error,
                }
            )
            logging.info("EIN %s -> %s (%s rows)", ein, status, len(records))

    audit_df = pd.DataFrame(audit_rows).sort_values(by=["status", "ein"]).reset_index(drop=True)
    return all_records, audit_df


def rename_columns(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    renamed = df.rename(columns={col: mapping.get(col, col) for col in df.columns})
    renamed.sort_index(axis=1, inplace=True)
    return renamed


def export_outputs(df: pd.DataFrame, audit_df: pd.DataFrame) -> tuple[Path, Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    date_tag = datetime.now().strftime("%Y%m%d")
    data_path = OUTPUT_DIR / f"all_nonprofits_data_{date_tag}.xlsx"
    audit_path = OUTPUT_DIR / f"bulk_harvest_audit_{date_tag}.csv"
    df.to_excel(data_path, index=False)
    audit_df.to_csv(audit_path, index=False, encoding="utf-8-sig")
    return data_path, audit_path


if __name__ == "__main__":
    print("====== Bulk GT Data Harvest ======")

    targets = get_targets_from_csv(CSV_FILE_PATH)
    if targets.empty:
        raise SystemExit("No valid EINs found in target CSV.")

    column_mapping = load_column_mapping(DICTIONARY_FILE_PATH, SHEET_NAME)
    all_companies_data, audit_df = fetch_all_targets(targets, workers=DEFAULT_WORKERS)

    if not all_companies_data:
        raise SystemExit("No data returned from GT API for the target list.")

    df = pd.DataFrame(all_companies_data)
    cleaned_df = rename_columns(df, column_mapping)
    data_path, audit_path = export_outputs(cleaned_df, audit_df)

    ok_count = int((audit_df["status"] == "ok").sum())
    empty_count = int((audit_df["status"] == "empty").sum())
    error_count = int((audit_df["status"] == "error").sum())

    print(f"Target EINs: {len(targets)}")
    print(f"Returned rows: {len(cleaned_df)}")
    print(f"API ok: {ok_count}")
    print(f"API empty: {empty_count}")
    print(f"API error: {error_count}")
    print(f"Saved combined export: {data_path}")
    print(f"Saved audit export: {audit_path}")