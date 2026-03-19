import argparse
import re
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd
import requests

BASE_URL = "https://990-infrastructure.gtdata.org/"
API_ENDPOINT = "irs-data/990basic120fields"

ROOT = Path(__file__).resolve().parents[1]
SOURCE_CSV = ROOT / "backend" / "data" / "nonprofits_100.csv"
TARGET_CSV = ROOT / "data_harvester" / "input" / "target_list.csv"
OUTPUT_DIR = ROOT / "data_harvester" / "output"

COMMON_WORDS = {
    "inc",
    "incorporated",
    "llc",
    "ltd",
    "foundation",
    "the",
    "of",
    "and",
    "co",
    "corp",
    "corporation",
    "association",
    "center",
    "centre",
    "community",
    "communities",
    "home",
    "services",
    "service",
    "retirement",
}


def normalize_ein(value) -> str:
    if value is None:
        return ""
    digits = "".join(ch for ch in str(value) if ch.isdigit())
    if not digits:
        return ""
    if len(digits) > 9:
        digits = digits[-9:]
    return digits.zfill(9)


def normalize_name(value: str) -> str:
    text = re.sub(r"[^a-z0-9 ]+", " ", str(value).lower())
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return ""
    tokens = [t for t in text.split(" ") if t and t not in COMMON_WORDS]
    if not tokens:
        tokens = text.split(" ")
    return " ".join(tokens)


def name_similarity(a: str, b: str) -> tuple:
    a_norm = normalize_name(a)
    b_norm = normalize_name(b)
    if not a_norm or not b_norm:
        return 0.0, 0.0

    ratio = SequenceMatcher(None, a_norm, b_norm).ratio()
    a_set = set(a_norm.split())
    b_set = set(b_norm.split())
    union = a_set | b_set
    jaccard = (len(a_set & b_set) / len(union)) if union else 0.0
    return ratio, jaccard


def ensure_target_copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def load_target_companies(target_csv: Path) -> pd.DataFrame:
    df = pd.read_csv(target_csv, skiprows=5, header=None)
    data = pd.DataFrame(
        {
            "company_name": df.iloc[:, 2].astype(str).str.strip(),
            "city": df.iloc[:, 4].astype(str).str.strip(),
            "st": df.iloc[:, 5].astype(str).str.strip(),
            "ein_raw": df.iloc[:, 8].astype(str).str.strip(),
        }
    )
    data["ein"] = data["ein_raw"].map(normalize_ein)
    data = data[(data["company_name"] != "") & (data["ein"] != "")].copy()
    data = data.drop_duplicates(subset=["ein"], keep="first")
    return data


def fetch_one(session: requests.Session, row, timeout: int) -> dict:
    ein = row.ein
    company_name = row.company_name

    status = "ok"
    error = ""
    result_count = 0
    org_name = ""
    latest_tax_year = ""
    total_revenue = ""

    try:
        resp = session.get(BASE_URL + API_ENDPOINT, params={"ein": ein}, timeout=timeout)
        resp.raise_for_status()
        payload = resp.json()
        results = payload.get("body", {}).get("results", []) if isinstance(payload, dict) else []
        if isinstance(results, list):
            result_count = len(results)
            if result_count > 0:
                top = results[0]
                org_name = str(top.get("FILERNAME1", ""))
                latest_tax_year = str(top.get("TAXYEAR", ""))
                total_revenue = str(top.get("TOTREVCURYEA", ""))
            else:
                status = "empty"
        else:
            status = "invalid_format"
            error = "body.results is not a list"
    except Exception as exc:
        status = "error"
        error = str(exc)

    ratio, jaccard = name_similarity(company_name, org_name)
    name_match = status == "ok" and (ratio >= 0.55 or jaccard >= 0.35)

    return {
        "ein": ein,
        "target_company": company_name,
        "target_city": row.city,
        "target_st": row.st,
        "api_status": status,
        "api_result_count": result_count,
        "api_org_name": org_name,
        "api_latest_tax_year": latest_tax_year,
        "api_total_revenue": total_revenue,
        "name_similarity_ratio": round(ratio, 4),
        "name_token_jaccard": round(jaccard, 4),
        "ein_and_name_match": bool(name_match),
        "error": error,
    }


def fetch_api(sample_df: pd.DataFrame, timeout: int, workers: int) -> pd.DataFrame:
    session = requests.Session()
    session.trust_env = False

    records = []
    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = [executor.submit(fetch_one, session, row, timeout) for row in sample_df.itertuples(index=False)]
        for future in as_completed(futures):
            records.append(future.result())

    api_df = pd.DataFrame(records)
    if not api_df.empty:
        api_df = api_df.sort_values(by=["ein"]).reset_index(drop=True)
    return api_df


def save_outputs(api_df: pd.DataFrame) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    api_df.to_csv(OUTPUT_DIR / "api_target_comparison.csv", index=False, encoding="utf-8-sig")

    outside_api_df = api_df[api_df["api_status"] != "ok"].copy()
    weak_name_df = api_df[(api_df["api_status"] == "ok") & (~api_df["ein_and_name_match"])].copy()

    outside_api_df.to_csv(OUTPUT_DIR / "target_not_found_in_api.csv", index=False, encoding="utf-8-sig")
    weak_name_df.to_csv(OUTPUT_DIR / "ein_hit_but_name_weak_match.csv", index=False, encoding="utf-8-sig")


def print_summary(total_target: int, api_df: pd.DataFrame, requested: int) -> None:
    checked = len(api_df)
    ok_count = int((api_df["api_status"] == "ok").sum()) if checked else 0
    empty_count = int((api_df["api_status"] == "empty").sum()) if checked else 0
    error_count = int((api_df["api_status"] == "error").sum()) if checked else 0
    ein_name_match_count = int(api_df["ein_and_name_match"].sum()) if checked else 0

    print("\n===== Target (nonprofits_100.csv) vs GiveTuesday API =====")
    print(f"Target unique companies (by EIN): {total_target}")
    print(f"Checked EINs: {checked} (requested: {requested})")
    print(f"EIN hit in API (status=ok): {ok_count}")
    print(f"EIN not found in API (empty): {empty_count}")
    print(f"API error: {error_count}")
    print(f"EIN coverage on checked set: {(ok_count / checked * 100) if checked else 0:.2f}%")
    print(f"EIN + company-name match: {ein_name_match_count}")
    print(f"EIN+name coverage on checked set: {(ein_name_match_count / checked * 100) if checked else 0:.2f}%")

    print("\nPreview (first 12 by EIN):")
    cols = [
        "ein",
        "target_company",
        "api_status",
        "api_result_count",
        "api_org_name",
        "name_similarity_ratio",
        "ein_and_name_match",
    ]
    print(api_df[cols].head(12).to_string(index=False))

    print("\nSaved files:")
    print(f"- {OUTPUT_DIR / 'api_target_comparison.csv'}")
    print(f"- {OUTPUT_DIR / 'target_not_found_in_api.csv'}")
    print(f"- {OUTPUT_DIR / 'ein_hit_but_name_weak_match.csv'}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare nonprofits_100.csv against GiveTuesday API by EIN and name.")
    parser.add_argument("--sample-size", type=int, default=0, help="How many target EINs to check. 0 means all.")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout seconds.")
    parser.add_argument("--workers", type=int, default=8, help="Concurrent workers for API calls.")
    args = parser.parse_args()

    if not SOURCE_CSV.exists():
        raise FileNotFoundError(f"Source CSV not found: {SOURCE_CSV}")

    ensure_target_copy(SOURCE_CSV, TARGET_CSV)
    target_df = load_target_companies(TARGET_CSV)

    if args.sample_size and args.sample_size > 0:
        sample_df = target_df.head(args.sample_size).copy()
        requested = args.sample_size
    else:
        sample_df = target_df.copy()
        requested = len(sample_df)

    api_df = fetch_api(sample_df, timeout=args.timeout, workers=args.workers)
    save_outputs(api_df)
    print_summary(total_target=len(target_df), api_df=api_df, requested=requested)


if __name__ == "__main__":
    main()