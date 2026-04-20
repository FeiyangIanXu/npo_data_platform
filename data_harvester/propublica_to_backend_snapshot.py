import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "output" / "propublica"
TARGET_CSV = SCRIPT_DIR.parent / "backend" / "data" / "nonprofits_100.csv"
FORM_TYPE_CODE_MAP = {
    "0": "990",
    "0.0": "990",
    "1": "990EO",
    "1.0": "990EO",
    "2": "990PF",
    "2.0": "990PF",
}


def latest_matching_file(pattern: str) -> Path:
    matches = sorted(OUTPUT_DIR.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"No files found for pattern: {pattern}")
    return matches[-1]


def parse_fiscal_month(value) -> Optional[int]:
    if pd.isna(value):
        return None
    text = str(value).strip()
    if text == "":
        return None
    digits = "".join(ch for ch in text if ch.isdigit())
    if len(digits) >= 6:
        try:
            month = int(digits[4:6])
            return month if 1 <= month <= 12 else None
        except ValueError:
            return None
    return None


def normalize_form_type(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text in {"", "nan", "None"}:
        return ""
    return FORM_TYPE_CODE_MAP.get(text, text)


def normalize_ein(value) -> str:
    if pd.isna(value):
        return ""
    digits = "".join(ch for ch in str(value) if ch.isdigit())
    if not digits:
        return ""
    return digits[-9:].zfill(9)


def load_target_lookup() -> pd.DataFrame:
    raw = pd.read_csv(TARGET_CSV, skiprows=5, header=None, dtype=str)
    lookup = pd.DataFrame(
        {
            "ein": raw.iloc[:, 8].apply(normalize_ein),
            "campus": raw.iloc[:, 2].astype(str).str.strip(),
            "city": raw.iloc[:, 4].astype(str).str.strip(),
            "st": raw.iloc[:, 5].astype(str).str.strip().str.upper(),
        }
    )
    lookup = lookup[lookup["ein"] != ""]
    return lookup.drop_duplicates(subset=["ein"], keep="first")


def build_backend_snapshot(snapshot_df: pd.DataFrame) -> pd.DataFrame:
    df = snapshot_df.copy()
    df["filing_date"] = pd.to_datetime(df["filing_date"], errors="coerce")
    df["fiscal_year"] = pd.to_numeric(df["tax_year"], errors="coerce").astype("Int64")
    df["fiscal_month"] = df["tax_prd"].apply(parse_fiscal_month).astype("Int64")
    df["ein"] = df["ein"].astype(str).str.zfill(9)

    backend_df = pd.DataFrame(
        {
            "ein": df["ein"],
            "campus": df["target_company"],
            "propublica_organization_name": df["organization_name"],
            "city": df["target_city"],
            "st": df["target_state"],
            "fiscal_year": df["fiscal_year"],
            "fiscal_month": df["fiscal_month"],
            "part_i_summary_12_total_revenue_cy": pd.to_numeric(df["total_revenue"], errors="coerce"),
            "part_ix_statement_of_functional_expenses_25_total_functional_expenses_cy": pd.to_numeric(
                df["total_expenses"], errors="coerce"
            ),
            "part_x_balance_sheet_16_total_assets_eoy": pd.to_numeric(df["total_assets"], errors="coerce"),
            "part_x_balance_sheet_22_net_assets_or_fund_balances_eoy": pd.to_numeric(
                df["net_assets"], errors="coerce"
            ),
            "employees": pd.to_numeric(df["employee_count"], errors="coerce"),
            "propublica_form_type": df["form_type"].apply(normalize_form_type),
            "propublica_filing_date": df["filing_date"],
            "propublica_tax_prd": df["tax_prd"],
            "propublica_record_status": df["record_status"],
            "propublica_filing_count": pd.to_numeric(df["filing_count"], errors="coerce"),
            "propublica_has_2024_plus": df["has_2024_plus"],
            "propublica_has_2025_plus": df["has_2025_plus"],
            "propublica_source": df["source"],
        }
    )
    return backend_df.sort_values(by=["propublica_record_status", "ein"]).reset_index(drop=True)


def build_backend_snapshot_from_filings(filings_df: pd.DataFrame) -> pd.DataFrame:
    df = filings_df.copy()
    df["ein"] = df["ein"].apply(normalize_ein)
    df["filing_date"] = pd.to_datetime(df["filing_date"], errors="coerce")
    df["fiscal_year"] = pd.to_numeric(df["tax_year"], errors="coerce").astype("Int64")
    df["fiscal_month"] = df["tax_prd"].apply(parse_fiscal_month).astype("Int64")
    df["raw_available"] = df["raw_available"].fillna(False).astype(bool)
    df = (
        df.sort_values(by=["ein", "fiscal_year", "filing_date"], ascending=[True, True, True])
        .drop_duplicates(subset=["ein", "fiscal_year"], keep="last")
        .reset_index(drop=True)
    )

    year_summary = (
        df[df["fiscal_year"].notna()]
        .groupby("ein")["fiscal_year"]
        .agg(
            propublica_filing_count="count",
            propublica_has_2024_plus=lambda years: bool((years >= 2024).any()),
            propublica_has_2025_plus=lambda years: bool((years >= 2025).any()),
        )
        .reset_index()
    )

    df = df.merge(load_target_lookup(), on="ein", how="left")
    df = df.merge(year_summary, on="ein", how="left")
    df["campus"] = df["campus"].fillna(df["organization_name"])
    df["city"] = df["city"].fillna("")
    df["st"] = df["st"].fillna("")

    backend_df = pd.DataFrame(
        {
            "ein": df["ein"],
            "campus": df["campus"],
            "propublica_organization_name": df["organization_name"],
            "city": df["city"],
            "st": df["st"],
            "fiscal_year": df["fiscal_year"],
            "fiscal_month": df["fiscal_month"],
            "part_i_summary_12_total_revenue_cy": pd.to_numeric(df["total_revenue"], errors="coerce"),
            "part_ix_statement_of_functional_expenses_25_total_functional_expenses_cy": pd.to_numeric(
                df["total_expenses"], errors="coerce"
            ),
            "part_x_balance_sheet_16_total_assets_eoy": pd.to_numeric(df["total_assets"], errors="coerce"),
            "part_x_balance_sheet_22_net_assets_or_fund_balances_eoy": pd.to_numeric(
                df["net_assets"], errors="coerce"
            ),
            "employees": pd.to_numeric(df["employee_count"], errors="coerce"),
            "propublica_form_type": df["form_type"].apply(normalize_form_type),
            "propublica_filing_date": df["filing_date"],
            "propublica_tax_prd": df["tax_prd"],
            "propublica_record_status": df["raw_available"].map({True: "ok", False: "missing_filing"}),
            "propublica_filing_count": pd.to_numeric(df["propublica_filing_count"], errors="coerce"),
            "propublica_has_2024_plus": df["propublica_has_2024_plus"].fillna(False),
            "propublica_has_2025_plus": df["propublica_has_2025_plus"].fillna(False),
            "propublica_source": df["source"],
        }
    )
    return backend_df.sort_values(by=["ein", "fiscal_year"], ascending=[True, False]).reset_index(drop=True)


def save_backend_snapshot(df: pd.DataFrame) -> tuple[Path, Path]:
    date_tag = datetime.now().strftime("%Y%m%d")
    csv_path = OUTPUT_DIR / f"propublica_backend_snapshot_{date_tag}.csv"
    xlsx_path = OUTPUT_DIR / f"propublica_backend_snapshot_{date_tag}.xlsx"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    excel_df = df.copy()
    if "propublica_filing_date" in excel_df.columns:
        excel_df["propublica_filing_date"] = pd.to_datetime(
            excel_df["propublica_filing_date"], errors="coerce"
        ).dt.tz_localize(None)
    try:
        excel_df.to_excel(xlsx_path, index=False)
    except PermissionError:
        time_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
        xlsx_path = OUTPUT_DIR / f"propublica_backend_snapshot_{time_tag}.xlsx"
        excel_df.to_excel(xlsx_path, index=False)
    return csv_path, xlsx_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert ProPublica latest snapshot into a backend-friendly schema.")
    parser.add_argument("--snapshot", type=str, default="", help="Optional latest snapshot CSV path.")
    parser.add_argument("--filings", type=str, default="", help="Optional yearly filings CSV path for full-history import.")
    args = parser.parse_args()

    if args.filings:
        input_path = Path(args.filings)
        source_label = "filings"
        filings_df = pd.read_csv(input_path, dtype={"ein": str})
        backend_df = build_backend_snapshot_from_filings(filings_df)
    else:
        input_path = Path(args.snapshot) if args.snapshot else latest_matching_file("propublica_latest_snapshot_*.csv")
        source_label = "snapshot"
        snapshot_df = pd.read_csv(input_path, dtype={"ein": str})
        backend_df = build_backend_snapshot(snapshot_df)

    csv_path, xlsx_path = save_backend_snapshot(backend_df)

    print("====== ProPublica Backend Snapshot ======")
    print(f"Input {source_label}: {input_path}")
    print(f"Rows exported: {len(backend_df)}")
    print(f"Saved CSV: {csv_path}")
    print(f"Saved XLSX: {xlsx_path}")


if __name__ == "__main__":
    main()
