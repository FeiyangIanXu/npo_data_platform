from datetime import datetime
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "output" / "propublica"


def latest_matching_file(pattern: str) -> Path:
    matches = sorted(OUTPUT_DIR.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"No files found for pattern: {pattern}")
    return matches[-1]


def build_yearly_export(df: pd.DataFrame) -> pd.DataFrame:
    yearly_first = [
        "ein",
        "target_company",
        "org_name",
        "filing_tax_prd_yr",
        "filing_tax_prd",
        "filing_formtype",
        "filing_updated",
        "filing_totrevenue",
        "filing_totfuncexpns",
        "filing_totassetsend",
        "filing_totliabend",
        "filing_totnetassetend",
    ]
    other_filing_cols = sorted([col for col in df.columns if col.startswith("filing_") and col not in yearly_first])
    org_cols = sorted([col for col in df.columns if col.startswith("org_") and col not in {"org_name"}])
    meta_cols = [col for col in ["api_version", "data_source"] if col in df.columns]

    ordered_cols = [col for col in yearly_first if col in df.columns] + other_filing_cols + org_cols + meta_cols
    export_df = df[ordered_cols].copy()
    if "filing_tax_prd_yr" in export_df.columns:
        export_df["filing_tax_prd_yr"] = pd.to_numeric(export_df["filing_tax_prd_yr"], errors="coerce").astype("Int64")
    export_df = export_df.sort_values(
        by=["ein", "filing_tax_prd_yr", "filing_tax_prd"],
        ascending=[True, False, False],
        na_position="last",
    ).reset_index(drop=True)
    return export_df


def save_outputs(export_df: pd.DataFrame) -> tuple[Path, Path]:
    date_tag = datetime.now().strftime("%Y%m%d")
    csv_path = OUTPUT_DIR / f"propublica_yearly_filings_full_{date_tag}.csv"
    xlsx_path = OUTPUT_DIR / f"propublica_yearly_filings_full_{date_tag}.xlsx"
    export_df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    excel_df = export_df.copy()
    if "filing_updated" in excel_df.columns:
        excel_df["filing_updated"] = pd.to_datetime(excel_df["filing_updated"], errors="coerce").dt.tz_localize(None)
    try:
        excel_df.to_excel(xlsx_path, index=False)
    except PermissionError:
        time_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
        xlsx_path = OUTPUT_DIR / f"propublica_yearly_filings_full_{time_tag}.xlsx"
        excel_df.to_excel(xlsx_path, index=False)
    return csv_path, xlsx_path


def main() -> None:
    candidates = sorted(
        path for path in OUTPUT_DIR.glob("propublica_all_fields_*.csv") if "audit" not in path.name.lower()
    )
    if not candidates:
        raise FileNotFoundError("No ProPublica full-field CSV found.")
    source_path = candidates[-1]
    df = pd.read_csv(source_path, dtype={"ein": str})
    export_df = build_yearly_export(df)
    csv_path, xlsx_path = save_outputs(export_df)

    print("====== ProPublica Yearly Filings Full Export ======")
    print(f"Input source: {source_path}")
    print(f"Rows exported: {len(export_df)}")
    print(f"Columns exported: {len(export_df.columns)}")
    print(f"Saved CSV: {csv_path}")
    print(f"Saved XLSX: {xlsx_path}")


if __name__ == "__main__":
    main()
