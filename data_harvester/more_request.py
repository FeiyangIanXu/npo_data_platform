import logging
from pathlib import Path

import pandas as pd
import requests


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BASE_URL = "https://990-infrastructure.gtdata.org/irs-data/"
OUTPUT_DIR = Path(__file__).resolve().parent / "output" / "gt" / "snapshots"
ENDPOINTS = {
    "bmf": "530196605",
    "efilexml": "842929872",
    "postcard": "000100514",
    "pub78-deductible": "000635913",
    "revoked": "000065837",
}


def build_session() -> requests.Session:
    session = requests.Session()
    session.trust_env = False
    return session


def payload_to_dataframe(payload) -> pd.DataFrame:
    if isinstance(payload, list):
        return pd.DataFrame(payload)
    if isinstance(payload, dict):
        body = payload.get("body", {})
        if isinstance(body, dict) and isinstance(body.get("results"), list):
            return pd.DataFrame(body["results"])
        return pd.DataFrame([payload])
    return pd.DataFrame()


def fetch_and_save_data(session: requests.Session, endpoint: str, ein: str, output_dir: Path) -> dict:
    output_path = output_dir / f"{endpoint}_{ein}.xlsx"
    logging.info("Fetching endpoint '%s' for EIN %s...", endpoint, ein)

    try:
        response = session.get(f"{BASE_URL}{endpoint}", params={"ein": ein}, timeout=30)
        response.raise_for_status()
        df = payload_to_dataframe(response.json())
        df.to_excel(output_path, index=False)
        logging.info("Saved %s rows to %s", len(df), output_path)
        return {"endpoint": endpoint, "ein": ein, "rows": len(df), "status": "ok", "output_file": str(output_path)}
    except requests.exceptions.RequestException as exc:
        logging.error("Request failed for endpoint '%s': %s", endpoint, exc)
        return {"endpoint": endpoint, "ein": ein, "rows": 0, "status": "error", "output_file": "", "error": str(exc)}
    except ValueError as exc:
        logging.error("JSON decode failed for endpoint '%s': %s", endpoint, exc)
        return {"endpoint": endpoint, "ein": ein, "rows": 0, "status": "error", "output_file": "", "error": str(exc)}


if __name__ == "__main__":
    print("====== GT Endpoint Snapshot ======")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    session = build_session()

    results = []
    for endpoint, ein in ENDPOINTS.items():
        results.append(fetch_and_save_data(session, endpoint, ein, OUTPUT_DIR))

    summary_df = pd.DataFrame(results)
    summary_path = OUTPUT_DIR / "endpoint_snapshot_summary.csv"
    summary_df.to_csv(summary_path, index=False, encoding="utf-8-sig")

    print(f"Endpoints checked: {len(results)}")
    print(f"Successful exports: {int((summary_df['status'] == 'ok').sum())}")
    print(f"Saved summary: {summary_path}")
