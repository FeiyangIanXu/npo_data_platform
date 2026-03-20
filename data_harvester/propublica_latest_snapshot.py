import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "output" / "propublica"
REPORT_DIR = OUTPUT_DIR / "reports"
TARGET_CSV = SCRIPT_DIR.parent / "backend" / "data" / "nonprofits_100.csv"


def latest_matching_file(pattern: str) -> Path:
    matches = sorted(OUTPUT_DIR.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"No files found for pattern: {pattern}")
    return matches[-1]


def normalize_ein_series(series: pd.Series) -> pd.Series:
    cleaned = series.where(series.notna(), "").astype(str).str.replace(r"\D", "", regex=True).str[-9:]
    cleaned = cleaned.where(cleaned != "", "").str.zfill(9)
    return cleaned.where(cleaned != "000000000", "")


def load_targets(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, skiprows=5, header=None)
    targets = pd.DataFrame(
        {
            "target_company": df.iloc[:, 2].astype(str).str.strip(),
            "target_city": df.iloc[:, 4].astype(str).str.strip(),
            "target_state": df.iloc[:, 5].astype(str).str.strip(),
            "ein": normalize_ein_series(df.iloc[:, 8]),
        }
    )
    targets = targets[(targets["target_company"] != "") & (targets["ein"] != "")]
    return targets.drop_duplicates(subset=["ein"], keep="first").reset_index(drop=True)


def load_filings(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"ein": str})
    df["ein"] = normalize_ein_series(df["ein"])
    df["tax_year"] = pd.to_numeric(df["tax_year"], errors="coerce").astype("Int64")
    df["filing_date"] = pd.to_datetime(df["filing_date"], errors="coerce")
    numeric_cols = ["total_revenue", "total_expenses", "total_assets", "net_assets", "employee_count"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def select_latest_filings(filings_df: pd.DataFrame) -> pd.DataFrame:
    working = filings_df.copy()
    working["form_type_sort"] = pd.to_numeric(working["form_type"], errors="coerce")
    working = working.sort_values(
        by=["ein", "tax_year", "filing_date", "form_type_sort"],
        ascending=[True, False, False, True],
        na_position="last",
    )
    latest = working.drop_duplicates(subset=["ein"], keep="first").reset_index(drop=True)
    latest["latest_available"] = latest["tax_year"].notna()
    latest["revenue_minus_expenses"] = latest["total_revenue"] - latest["total_expenses"]
    latest["asset_minus_net_assets"] = latest["total_assets"] - latest["net_assets"]
    return latest.drop(columns=["form_type_sort"])


def build_snapshot(targets_df: pd.DataFrame, latest_df: pd.DataFrame, audit_df: pd.DataFrame) -> pd.DataFrame:
    audit_subset = audit_df[
        [
            "ein",
            "status",
            "filing_count",
            "latest_tax_year",
            "has_2024_plus",
            "has_2025_plus",
        ]
    ].copy()
    audit_subset["ein"] = normalize_ein_series(audit_subset["ein"])
    merged = targets_df.merge(latest_df, on="ein", how="left", suffixes=("", "_latest"))
    merged = merged.merge(audit_subset, on="ein", how="left")

    merged["organization_name"] = merged["organization_name"].fillna(merged["target_company"])
    merged["record_status"] = merged["status"].fillna("missing")
    merged["latest_tax_year"] = pd.to_numeric(merged["latest_tax_year"], errors="coerce").astype("Int64")
    merged["tax_year"] = pd.to_numeric(merged["tax_year"], errors="coerce").astype("Int64")
    return merged[
        [
            "ein",
            "target_company",
            "organization_name",
            "target_city",
            "target_state",
            "record_status",
            "filing_count",
            "tax_year",
            "latest_tax_year",
            "has_2024_plus",
            "has_2025_plus",
            "filing_date",
            "tax_prd",
            "form_type",
            "total_revenue",
            "total_expenses",
            "revenue_minus_expenses",
            "total_assets",
            "net_assets",
            "asset_minus_net_assets",
            "employee_count",
            "source",
            "raw_available",
        ]
    ].sort_values(by=["record_status", "ein"]).reset_index(drop=True)


def save_snapshot(snapshot_df: pd.DataFrame) -> tuple[Path, Path]:
    date_tag = datetime.now().strftime("%Y%m%d")
    csv_path = OUTPUT_DIR / f"propublica_latest_snapshot_{date_tag}.csv"
    xlsx_path = OUTPUT_DIR / f"propublica_latest_snapshot_{date_tag}.xlsx"
    snapshot_df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    excel_df = snapshot_df.copy()
    if "filing_date" in excel_df.columns:
        excel_df["filing_date"] = pd.to_datetime(excel_df["filing_date"], errors="coerce").dt.tz_localize(None)
    try:
        excel_df.to_excel(xlsx_path, index=False)
    except PermissionError:
        time_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
        xlsx_path = OUTPUT_DIR / f"propublica_latest_snapshot_{time_tag}.xlsx"
        excel_df.to_excel(xlsx_path, index=False)
    return csv_path, xlsx_path


def save_report(snapshot_df: pd.DataFrame) -> Path:
    date_tag = datetime.now().strftime("%Y%m%d")
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"ProPublica_Latest_Snapshot_Report_{date_tag}.md"
    status_counts = snapshot_df["record_status"].fillna("missing").value_counts().to_dict()
    year_counts = snapshot_df["tax_year"].dropna().astype(int).value_counts().sort_index(ascending=False).to_dict()
    top_2024 = snapshot_df[snapshot_df["tax_year"] >= 2024][["ein", "target_company", "tax_year"]]

    has_2024_plus_count = int(pd.to_numeric(snapshot_df["has_2024_plus"], errors="coerce").fillna(0).sum())
    has_2025_plus_count = int(pd.to_numeric(snapshot_df["has_2025_plus"], errors="coerce").fillna(0).sum())

    lines = [
        "# ProPublica Latest Snapshot Report",
        "",
        "## Summary",
        "",
        f"- Total target EINs: {len(snapshot_df)}",
        f"- Records with latest filing selected: {int(snapshot_df['tax_year'].notna().sum())}",
        f"- EINs with 2024+: {has_2024_plus_count}",
        f"- EINs with 2025+: {has_2025_plus_count}",
        "",
        "## Status Distribution",
        "",
    ]
    for status, count in sorted(status_counts.items()):
        lines.append(f"- {status}: {count}")
    lines.extend(["", "## Latest Tax Year Distribution", ""])
    for year, count in year_counts.items():
        lines.append(f"- {year}: {count}")
    lines.extend(["", "## 2024+ Organizations", ""])
    if top_2024.empty:
        lines.append("- None")
    else:
        for row in top_2024.itertuples(index=False):
            lines.append(f"- `{row.ein}` - {row.target_company} ({int(row.tax_year)})")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build latest-filing ProPublica snapshot from existing harvest outputs.")
    parser.add_argument("--filings", type=str, default="", help="Optional filings CSV path.")
    parser.add_argument("--audit", type=str, default="", help="Optional audit CSV path.")
    args = parser.parse_args()

    filings_path = Path(args.filings) if args.filings else latest_matching_file("propublica_filings_*.csv")
    audit_path = Path(args.audit) if args.audit else latest_matching_file("propublica_audit_*.csv")

    targets_df = load_targets(TARGET_CSV)
    filings_df = load_filings(filings_path)
    audit_df = pd.read_csv(audit_path, dtype={"ein": str})
    latest_df = select_latest_filings(filings_df)
    snapshot_df = build_snapshot(targets_df, latest_df, audit_df)
    csv_path, xlsx_path = save_snapshot(snapshot_df)
    report_path = save_report(snapshot_df)

    print("====== ProPublica Latest Snapshot ======")
    print(f"Input filings: {filings_path}")
    print(f"Input audit: {audit_path}")
    print(f"Snapshot rows: {len(snapshot_df)}")
    print(f"Rows with latest filing: {int(snapshot_df['tax_year'].notna().sum())}")
    print(f"Saved snapshot CSV: {csv_path}")
    print(f"Saved snapshot XLSX: {xlsx_path}")
    print(f"Saved report MD: {report_path}")


if __name__ == "__main__":
    main()
