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
FIRST100_PATH = ROOT_DIR / "backend" / "data" / "First100.xlsx"


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
    for pattern in [r"(\d{4})-\d{2}-\d{2}", r"(\d{4})/\d{1,2}/\d{1,2}", r"\d{1,2}/(\d{4})"]:
        match = re.search(pattern, text)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
    return None


def load_first100(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, header=None)
    data = df.iloc[5:].copy().reset_index(drop=True)
    manual_df = pd.DataFrame(
        {
            "ein": data.iloc[:, 8].map(normalize_ein),
            "manual_campus": data.iloc[:, 2].astype(str).str.strip(),
            "manual_city": data.iloc[:, 4].astype(str).str.strip(),
            "manual_st": data.iloc[:, 5].astype(str).str.strip(),
            "manual_fiscal_year": data.iloc[:, 6].apply(parse_fiscal_year),
            "manual_filed_on_date": pd.to_datetime(data.iloc[:, 7], errors="coerce"),
            "manual_gross_receipts": pd.to_numeric(data.iloc[:, 9], errors="coerce"),
            "manual_employees": pd.to_numeric(data.iloc[:, 14], errors="coerce"),
            "manual_total_revenue_cy": pd.to_numeric(data.iloc[:, 25], errors="coerce"),
            "manual_total_expenses_cy": pd.to_numeric(data.iloc[:, 34], errors="coerce"),
            "manual_total_assets_cy": pd.to_numeric(data.iloc[:, 38], errors="coerce"),
            "manual_net_assets_cy": pd.to_numeric(data.iloc[:, 42], errors="coerce"),
        }
    )
    manual_df = manual_df[(manual_df["manual_campus"] != "") & (manual_df["ein"] != "")]
    return manual_df.drop_duplicates(subset=["ein"], keep="first").reset_index(drop=True)


def load_propublica_snapshot(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"ein": str})
    df["ein"] = df["ein"].map(normalize_ein)
    df["tax_year"] = pd.to_numeric(df["tax_year"], errors="coerce").astype("Int64")
    df["total_revenue"] = pd.to_numeric(df["total_revenue"], errors="coerce")
    df["total_expenses"] = pd.to_numeric(df["total_expenses"], errors="coerce")
    df["total_assets"] = pd.to_numeric(df["total_assets"], errors="coerce")
    df["net_assets"] = pd.to_numeric(df["net_assets"], errors="coerce")
    df["employee_count"] = pd.to_numeric(df["employee_count"], errors="coerce")
    return df


def diff_metrics(left: pd.Series, right: pd.Series) -> tuple[pd.Series, pd.Series]:
    abs_diff = (left - right).abs()
    pct_diff = abs_diff / right.abs().replace(0, pd.NA)
    return abs_diff, pct_diff


def build_comparison(manual_df: pd.DataFrame, pro_df: pd.DataFrame) -> pd.DataFrame:
    merged = manual_df.merge(pro_df, on="ein", how="outer")
    merged["name_similarity"] = merged.apply(
        lambda row: name_similarity(row.get("manual_campus", ""), row.get("organization_name", "")),
        axis=1,
    )
    merged["city_match"] = (
        merged["manual_city"].fillna("").str.upper() == merged["target_city"].fillna("").str.upper()
    )
    merged["state_match"] = merged["manual_st"].fillna("").str.upper() == merged["target_state"].fillna("").str.upper()
    merged["fiscal_year_diff"] = (
        pd.to_numeric(merged["tax_year"], errors="coerce") - pd.to_numeric(merged["manual_fiscal_year"], errors="coerce")
    )

    pairs = [
        ("total_revenue", "manual_total_revenue_cy", "revenue"),
        ("total_expenses", "manual_total_expenses_cy", "expenses"),
        ("total_assets", "manual_total_assets_cy", "assets"),
        ("net_assets", "manual_net_assets_cy", "net_assets"),
        ("employee_count", "manual_employees", "employees"),
    ]
    for pro_col, manual_col, prefix in pairs:
        abs_diff, pct_diff = diff_metrics(
            pd.to_numeric(merged[pro_col], errors="coerce"),
            pd.to_numeric(merged[manual_col], errors="coerce"),
        )
        merged[f"{prefix}_abs_diff"] = abs_diff
        merged[f"{prefix}_pct_diff"] = pct_diff

    def classify(row) -> str:
        if pd.isna(row.get("tax_year")):
            return "missing_propublica"
        if pd.isna(row.get("manual_fiscal_year")):
            return "missing_manual"
        if row.get("name_similarity", 0) < 0.6:
            return "possible_entity_mismatch"
        if pd.notna(row.get("revenue_pct_diff")) and row["revenue_pct_diff"] > 0.5:
            return "large_revenue_gap"
        fiscal_year_diff = row.get("fiscal_year_diff")
        if pd.notna(fiscal_year_diff) and fiscal_year_diff != 0:
            return "year_difference"
        return "generally_aligned"

    merged["comparison_status"] = merged.apply(classify, axis=1)
    return merged.sort_values(by=["comparison_status", "ein"]).reset_index(drop=True)


def save_outputs(comparison_df: pd.DataFrame) -> tuple[Path, Path]:
    date_tag = datetime.now().strftime("%Y%m%d")
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = REPORT_DIR / f"propublica_vs_first100_{date_tag}.csv"
    report_path = REPORT_DIR / f"ProPublica_vs_First100_Report_{date_tag}.md"
    comparison_df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    status_counts = comparison_df["comparison_status"].value_counts().to_dict()
    avg_similarity = comparison_df["name_similarity"].dropna().mean()
    mean_revenue_pct_diff = comparison_df["revenue_pct_diff"].dropna().mean()
    flagged = comparison_df[
        comparison_df["comparison_status"].isin(["possible_entity_mismatch", "large_revenue_gap"])
    ][["ein", "manual_campus", "organization_name", "comparison_status", "name_similarity", "revenue_pct_diff"]]

    lines = [
        "# ProPublica vs First100 Comparison Report",
        "",
        "## Summary",
        "",
        f"- Manual benchmark rows: {int(comparison_df['manual_campus'].notna().sum())}",
        f"- ProPublica rows compared: {int(comparison_df['tax_year'].notna().sum())}",
        f"- Average name similarity: {avg_similarity:.4f}" if pd.notna(avg_similarity) else "- Average name similarity: N/A",
        (
            f"- Mean revenue pct diff: {mean_revenue_pct_diff:.4f}"
            if pd.notna(mean_revenue_pct_diff)
            else "- Mean revenue pct diff: N/A"
        ),
        "",
        "## Status Counts",
        "",
    ]
    for status, count in sorted(status_counts.items()):
        lines.append(f"- {status}: {count}")
    lines.extend(["", "## Flagged Samples", ""])
    if flagged.empty:
        lines.append("- None")
    else:
        for row in flagged.head(15).itertuples(index=False):
            rev_pct = row.revenue_pct_diff
            rev_pct_text = f"{rev_pct:.4f}" if pd.notna(rev_pct) else "N/A"
            lines.append(
                f"- `{row.ein}` - {row.manual_campus} vs {row.organization_name} | {row.comparison_status} | "
                f"name_similarity={row.name_similarity:.4f} | revenue_pct_diff={rev_pct_text}"
            )

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return csv_path, report_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare ProPublica latest snapshot against manual First100 benchmark.")
    parser.add_argument("--snapshot", type=str, default="", help="Optional ProPublica latest snapshot CSV path.")
    args = parser.parse_args()

    snapshot_path = Path(args.snapshot) if args.snapshot else latest_matching_file("propublica_latest_snapshot_*.csv")
    manual_df = load_first100(FIRST100_PATH)
    pro_df = load_propublica_snapshot(snapshot_path)
    comparison_df = build_comparison(manual_df, pro_df)
    csv_path, report_path = save_outputs(comparison_df)

    print("====== ProPublica vs First100 Comparison ======")
    print(f"Manual input: {FIRST100_PATH}")
    print(f"ProPublica input: {snapshot_path}")
    print(f"Rows compared: {len(comparison_df)}")
    print(f"Saved CSV: {csv_path}")
    print(f"Saved report: {report_path}")


if __name__ == "__main__":
    main()
