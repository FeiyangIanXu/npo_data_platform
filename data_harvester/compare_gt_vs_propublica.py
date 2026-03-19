import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "output"
GT_COMPARISON_PATH = OUTPUT_DIR / "api_target_comparison.csv"


def latest_matching_file(pattern: str) -> Path:
    matches = sorted(OUTPUT_DIR.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"No files found for pattern: {pattern}")
    return matches[-1]


def load_gt_latest_years(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"ein": str})
    df["ein"] = df["ein"].astype(str).str.zfill(9)
    df["gt_latest_tax_year"] = pd.to_numeric(df["api_latest_tax_year"], errors="coerce").astype("Int64")
    return df[["ein", "target_company", "gt_latest_tax_year"]].drop_duplicates(subset=["ein"])


def load_propublica_latest_years(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"ein": str})
    df["ein"] = df["ein"].astype(str).str.zfill(9)
    df["propublica_latest_tax_year"] = pd.to_numeric(df["latest_tax_year"], errors="coerce").astype("Int64")
    return df[
        [
            "ein",
            "target_company",
            "status",
            "propublica_latest_tax_year",
            "has_2024_plus",
            "has_2025_plus",
        ]
    ].drop_duplicates(subset=["ein"])


def build_comparison(gt_df: pd.DataFrame, pro_df: pd.DataFrame) -> pd.DataFrame:
    merged = gt_df.merge(pro_df, on="ein", how="outer", suffixes=("_gt", "_pro"))
    merged["target_company"] = merged["target_company_gt"].fillna(merged["target_company_pro"])
    merged["gt_missing"] = merged["gt_latest_tax_year"].isna()
    merged["propublica_missing"] = merged["propublica_latest_tax_year"].isna()
    merged["year_delta"] = (
        merged["propublica_latest_tax_year"].astype("Float64") - merged["gt_latest_tax_year"].astype("Float64")
    )
    merged["propublica_newer"] = merged["year_delta"].fillna(-999) > 0

    def status(row) -> str:
        if row["gt_missing"] and row["propublica_missing"]:
            return "missing_both"
        if row["gt_missing"]:
            return "only_propublica"
        if row["propublica_missing"]:
            return "only_gt"
        if row["propublica_newer"]:
            return "propublica_newer"
        if row["year_delta"] == 0:
            return "same_latest_year"
        return "gt_newer_or_mismatch"

    merged["comparison_status"] = merged.apply(status, axis=1)
    return merged[
        [
            "ein",
            "target_company",
            "gt_latest_tax_year",
            "propublica_latest_tax_year",
            "year_delta",
            "propublica_newer",
            "gt_missing",
            "propublica_missing",
            "has_2024_plus",
            "has_2025_plus",
            "status",
            "comparison_status",
        ]
    ].sort_values(by=["comparison_status", "ein"]).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare GT latest tax year against ProPublica latest tax year.")
    parser.add_argument(
        "--propublica-audit",
        type=str,
        default="",
        help="Optional explicit ProPublica audit CSV path. Defaults to latest propublica_audit_*.csv.",
    )
    args = parser.parse_args()

    pro_path = Path(args.propublica_audit) if args.propublica_audit else latest_matching_file("propublica_audit_*.csv")
    gt_df = load_gt_latest_years(GT_COMPARISON_PATH)
    pro_df = load_propublica_latest_years(pro_path)
    comparison_df = build_comparison(gt_df, pro_df)

    date_tag = datetime.now().strftime("%Y%m%d")
    output_path = OUTPUT_DIR / f"gt_vs_propublica_freshness_{date_tag}.csv"
    try:
        comparison_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    except PermissionError:
        time_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = OUTPUT_DIR / f"gt_vs_propublica_freshness_{time_tag}.csv"
        comparison_df.to_csv(output_path, index=False, encoding="utf-8-sig")

    newer_count = int(comparison_df["propublica_newer"].sum())
    same_count = int((comparison_df["comparison_status"] == "same_latest_year").sum())
    print("====== GT vs ProPublica Freshness Comparison ======")
    print(f"GT input: {GT_COMPARISON_PATH}")
    print(f"ProPublica input: {pro_path}")
    print(f"Compared EINs: {len(comparison_df)}")
    print(f"ProPublica newer: {newer_count}")
    print(f"Same latest year: {same_count}")
    print(f"Saved comparison CSV: {output_path}")


if __name__ == "__main__":
    main()
