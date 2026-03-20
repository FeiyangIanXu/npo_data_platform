import argparse
import re
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Optional

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
PROPUBLICA_OUTPUT_DIR = SCRIPT_DIR / "output" / "propublica"
REPORT_DIR = PROPUBLICA_OUTPUT_DIR / "reports"
NONPROFITS_CSV_PATH = ROOT_DIR / "backend" / "data" / "nonprofits_100.csv"


def latest_matching_file(pattern: str) -> Path:
    matches = sorted(PROPUBLICA_OUTPUT_DIR.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"No files found for pattern: {pattern}")
    return matches[-1]


def normalize_ein(value) -> str:
    if pd.isna(value):
        return ""
    digits = re.sub(r"\D", "", str(value))
    if not digits:
        return ""
    if len(digits) > 9:
        digits = digits[-9:]
    return digits.zfill(9)


def normalize_name(value: str) -> str:
    text = re.sub(r"[^a-z0-9 ]+", " ", str(value).lower())
    return re.sub(r"\s+", " ", text).strip()


def name_similarity(a: str, b: str) -> float:
    a_norm = normalize_name(a)
    b_norm = normalize_name(b)
    if not a_norm or not b_norm:
        return 0.0
    return round(SequenceMatcher(None, a_norm, b_norm).ratio(), 4)


def parse_fiscal_year(value) -> Optional[int]:
    if pd.isna(value):
        return None
    text = str(value).strip()
    if not text:
        return None
    if re.fullmatch(r"\d{1,2}/\d{4}", text):
        return int(text[-4:])
    match = re.search(r"(\d{4})[-/]\d{1,2}[-/]\d{1,2}", text)
    if match:
        return int(match.group(1))
    return None


def parse_numeric(value) -> Optional[float]:
    if pd.isna(value):
        return None
    text = str(value).strip().replace("$", "").replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def load_cleaned_benchmark(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, skiprows=5, header=None)
    benchmark_df = pd.DataFrame(
        {
            "ein": df.iloc[:, 8].map(normalize_ein),
            "benchmark_campus": df.iloc[:, 2].astype(str).str.strip(),
            "benchmark_city": df.iloc[:, 4].astype(str).str.strip(),
            "benchmark_st": df.iloc[:, 5].astype(str).str.strip(),
            "benchmark_fiscal_year": df.iloc[:, 6].apply(parse_fiscal_year),
            "benchmark_filed_on_date": df.iloc[:, 7].astype(str).str.strip(),
            "benchmark_gross_receipts": df.iloc[:, 9].apply(parse_numeric),
            "benchmark_employees": pd.to_numeric(df.iloc[:, 14], errors="coerce"),
            "benchmark_total_revenue_cy": df.iloc[:, 25].apply(parse_numeric),
            "benchmark_total_expenses_cy": df.iloc[:, 34].apply(parse_numeric),
            "benchmark_total_assets_cy": df.iloc[:, 38].apply(parse_numeric),
            "benchmark_net_assets_cy": df.iloc[:, 42].apply(parse_numeric),
        }
    )
    benchmark_df = benchmark_df[(benchmark_df["benchmark_campus"] != "") & (benchmark_df["ein"] != "")]
    return benchmark_df.drop_duplicates(subset=["ein"], keep="first").reset_index(drop=True)


def load_propublica_snapshot(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"ein": str})
    df["ein"] = df["ein"].map(normalize_ein)
    numeric_cols = [
        "tax_year",
        "total_revenue",
        "total_expenses",
        "total_assets",
        "net_assets",
        "employee_count",
        "filing_count",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def load_propublica_yearly_filings(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"ein": str})
    df["ein"] = df["ein"].map(normalize_ein)
    numeric_cols = ["tax_year", "total_revenue", "total_expenses", "total_assets", "net_assets", "employee_count"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def diff_metrics(left: pd.Series, right: pd.Series) -> tuple[pd.Series, pd.Series]:
    abs_diff = (left - right).abs()
    pct_diff = abs_diff / right.abs().replace(0, pd.NA)
    return abs_diff, pct_diff


def build_comparison(benchmark_df: pd.DataFrame, pro_latest_df: pd.DataFrame, pro_yearly_df: pd.DataFrame) -> pd.DataFrame:
    matched_year_df = pro_yearly_df.rename(
        columns={
            "organization_name": "matched_organization_name",
            "tax_year": "matched_tax_year",
            "total_revenue": "matched_total_revenue",
            "total_expenses": "matched_total_expenses",
            "total_assets": "matched_total_assets",
            "net_assets": "matched_net_assets",
            "employee_count": "matched_employee_count",
            "filing_date": "matched_filing_date",
            "tax_prd": "matched_tax_prd",
            "form_type": "matched_form_type",
            "source": "matched_source",
            "raw_available": "matched_raw_available",
        }
    )
    matched_year_df["benchmark_fiscal_year"] = pd.to_numeric(matched_year_df["matched_tax_year"], errors="coerce")
    merged = benchmark_df.merge(
        matched_year_df,
        on=["ein", "benchmark_fiscal_year"],
        how="left",
    )
    latest_subset = pro_latest_df.rename(
        columns={
            "organization_name": "latest_organization_name",
            "target_city": "latest_target_city",
            "target_state": "latest_target_state",
            "tax_year": "latest_tax_year",
            "total_revenue": "latest_total_revenue",
            "total_expenses": "latest_total_expenses",
            "total_assets": "latest_total_assets",
            "net_assets": "latest_net_assets",
            "employee_count": "latest_employee_count",
            "filing_date": "latest_filing_date",
            "tax_prd": "latest_tax_prd",
            "form_type": "latest_form_type",
            "source": "latest_source",
            "raw_available": "latest_raw_available",
            "record_status": "latest_record_status",
        }
    )
    merged = merged.merge(
        latest_subset[
            [
                "ein",
                "latest_organization_name",
                "latest_target_city",
                "latest_target_state",
                "latest_tax_year",
                "latest_total_revenue",
                "latest_total_expenses",
                "latest_total_assets",
                "latest_net_assets",
                "latest_employee_count",
                "latest_filing_date",
                "latest_tax_prd",
                "latest_form_type",
                "latest_source",
                "latest_raw_available",
                "latest_record_status",
            ]
        ],
        on="ein",
        how="left",
        suffixes=("", "_drop"),
    )
    merged = merged.loc[:, ~merged.columns.duplicated()].copy()
    if "record_status_drop" in merged.columns:
        merged = merged.drop(columns=["record_status_drop"])
    merged["organization_name"] = merged["matched_organization_name"].fillna(merged["latest_organization_name"])
    merged["target_city"] = merged["latest_target_city"]
    merged["target_state"] = merged["latest_target_state"]
    merged["name_similarity"] = merged.apply(
        lambda row: name_similarity(row["benchmark_campus"], row.get("organization_name", "")),
        axis=1,
    )
    merged["city_match"] = (
        merged["benchmark_city"].fillna("").str.upper() == merged["target_city"].fillna("").str.upper()
    )
    merged["state_match"] = (
        merged["benchmark_st"].fillna("").str.upper() == merged["target_state"].fillna("").str.upper()
    )
    merged["latest_minus_benchmark_year"] = pd.to_numeric(merged["latest_tax_year"], errors="coerce") - pd.to_numeric(
        merged["benchmark_fiscal_year"], errors="coerce"
    )
    merged["year_match_status"] = merged.apply(
        lambda row: "matched_exact_year"
        if pd.notna(row.get("matched_tax_year"))
        else ("propublica_has_newer_year" if pd.notna(row.get("latest_tax_year")) else "missing_propublica"),
        axis=1,
    )

    metric_pairs = [
        ("matched_total_revenue", "benchmark_total_revenue_cy", "revenue"),
        ("matched_total_expenses", "benchmark_total_expenses_cy", "expenses"),
        ("matched_total_assets", "benchmark_total_assets_cy", "assets"),
        ("matched_net_assets", "benchmark_net_assets_cy", "net_assets"),
        ("matched_employee_count", "benchmark_employees", "employees"),
    ]
    for pro_col, bench_col, prefix in metric_pairs:
        abs_diff, pct_diff = diff_metrics(
            pd.to_numeric(merged[pro_col], errors="coerce"),
            pd.to_numeric(merged[bench_col], errors="coerce"),
        )
        merged[f"{prefix}_abs_diff"] = abs_diff
        merged[f"{prefix}_pct_diff"] = pct_diff

    def classify(row) -> str:
        if pd.isna(row.get("latest_tax_year")):
            return "missing_propublica"
        if pd.isna(row.get("matched_tax_year")):
            return "missing_matching_year"
        if row.get("name_similarity", 0) < 0.6:
            return "possible_entity_mismatch"
        if pd.notna(row.get("revenue_pct_diff")) and row["revenue_pct_diff"] > 0.5:
            return "large_revenue_gap"
        return "generally_aligned"

    merged["comparison_status"] = merged.apply(classify, axis=1)
    merged["field_match_summary"] = merged.apply(
        lambda row: summarize_field_match(row),
        axis=1,
    )
    return merged.sort_values(by=["comparison_status", "ein"]).reset_index(drop=True)


def summarize_field_match(row: pd.Series) -> str:
    checks = []
    for label in ["revenue", "expenses", "assets", "net_assets", "employees"]:
        pct = row.get(f"{label}_pct_diff")
        if pd.isna(pct):
            checks.append(f"{label}:na")
        elif pct <= 0.05:
            checks.append(f"{label}:tight")
        elif pct <= 0.20:
            checks.append(f"{label}:close")
        else:
            checks.append(f"{label}:wide")
    return "; ".join(checks)


def build_review_list(comparison_df: pd.DataFrame) -> pd.DataFrame:
    review_df = comparison_df[
        comparison_df["comparison_status"].isin(
            ["possible_entity_mismatch", "large_revenue_gap", "missing_matching_year", "missing_propublica"]
        )
    ].copy()
    review_df["discussion_priority"] = review_df["comparison_status"].map(
        {
            "possible_entity_mismatch": "high",
            "large_revenue_gap": "high",
            "missing_matching_year": "medium",
            "missing_propublica": "medium",
        }
    )
    return review_df[
        [
            "ein",
            "benchmark_campus",
            "organization_name",
            "comparison_status",
            "discussion_priority",
            "name_similarity",
            "benchmark_fiscal_year",
            "matched_tax_year",
            "latest_tax_year",
            "latest_minus_benchmark_year",
            "year_match_status",
            "benchmark_total_revenue_cy",
            "matched_total_revenue",
            "revenue_pct_diff",
            "benchmark_total_expenses_cy",
            "matched_total_expenses",
            "expenses_pct_diff",
            "benchmark_total_assets_cy",
            "matched_total_assets",
            "assets_pct_diff",
            "benchmark_net_assets_cy",
            "matched_net_assets",
            "net_assets_pct_diff",
            "benchmark_employees",
            "matched_employee_count",
            "employees_pct_diff",
            "city_match",
            "state_match",
            "field_match_summary",
            "latest_record_status",
        ]
    ].sort_values(by=["discussion_priority", "comparison_status", "ein"]).reset_index(drop=True)


def save_outputs(comparison_df: pd.DataFrame, review_df: pd.DataFrame) -> tuple[Path, Path, Path]:
    date_tag = datetime.now().strftime("%Y%m%d")
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    comparison_path = REPORT_DIR / f"propublica_vs_nonprofits_csv_matched_year_{date_tag}.csv"
    review_path = REPORT_DIR / f"propublica_review_list_matched_year_{date_tag}.csv"
    report_path = REPORT_DIR / f"ProPublica_Review_Report_Matched_Year_{date_tag}.md"

    comparison_df.to_csv(comparison_path, index=False, encoding="utf-8-sig")
    review_df.to_csv(review_path, index=False, encoding="utf-8-sig")

    status_counts = comparison_df["comparison_status"].value_counts().to_dict()
    lines = [
        "# ProPublica Review Report",
        "",
        "## Summary",
        "",
        f"- Benchmark rows: {len(comparison_df)}",
        f"- Review rows: {len(review_df)}",
        "",
        "## Status Counts",
        "",
    ]
    for status, count in sorted(status_counts.items()):
        lines.append(f"- {status}: {count}")
    lines.extend(["", "## High Priority Samples", ""])
    high_priority = review_df[review_df["discussion_priority"] == "high"].head(20)
    if high_priority.empty:
        lines.append("- None")
    else:
        for row in high_priority.itertuples(index=False):
            revenue_text = f"{row.revenue_pct_diff:.4f}" if pd.notna(row.revenue_pct_diff) else "N/A"
            lines.append(
                f"- `{row.ein}` - {row.benchmark_campus} vs {row.organization_name} | {row.comparison_status} | "
                f"name_similarity={row.name_similarity:.4f} | revenue_pct_diff={revenue_text} | "
                f"field_match={row.field_match_summary}"
            )

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return comparison_path, review_path, report_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare ProPublica latest snapshot with cleaned nonprofits_100.csv.")
    parser.add_argument("--snapshot", type=str, default="", help="Optional ProPublica latest snapshot CSV path.")
    parser.add_argument("--yearly-filings", type=str, default="", help="Optional ProPublica yearly filings CSV path.")
    args = parser.parse_args()

    snapshot_path = Path(args.snapshot) if args.snapshot else latest_matching_file("propublica_latest_snapshot_*.csv")
    yearly_filings_path = (
        Path(args.yearly_filings) if args.yearly_filings else latest_matching_file("propublica_filings_*.csv")
    )
    benchmark_df = load_cleaned_benchmark(NONPROFITS_CSV_PATH)
    pro_latest_df = load_propublica_snapshot(snapshot_path)
    pro_yearly_df = load_propublica_yearly_filings(yearly_filings_path)
    comparison_df = build_comparison(benchmark_df, pro_latest_df, pro_yearly_df)
    review_df = build_review_list(comparison_df)
    comparison_path, review_path, report_path = save_outputs(comparison_df, review_df)

    print("====== ProPublica vs Cleaned nonprofits_100.csv (Matched Year) ======")
    print(f"Benchmark input: {NONPROFITS_CSV_PATH}")
    print(f"ProPublica input: {snapshot_path}")
    print(f"ProPublica yearly input: {yearly_filings_path}")
    print(f"Comparison rows: {len(comparison_df)}")
    print(f"Review rows: {len(review_df)}")
    print(f"Saved comparison CSV: {comparison_path}")
    print(f"Saved review CSV: {review_path}")
    print(f"Saved report MD: {report_path}")


if __name__ == "__main__":
    main()
