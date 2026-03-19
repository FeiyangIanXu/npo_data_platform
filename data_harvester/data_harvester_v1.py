import json
import logging

import pandas as pd
import requests

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = "https://990-infrastructure.gtdata.org/"
TEST_EIN = "842929872"  # Legacy sample EIN in this script


def build_session() -> requests.Session:
    session = requests.Session()
    # Ignore broken environment proxy variables by default.
    session.trust_env = False
    return session


def extract_results(payload: dict) -> list:
    if not isinstance(payload, dict):
        return []
    body = payload.get("body", {})
    if not isinstance(body, dict):
        return []
    results = body.get("results", [])
    return results if isinstance(results, list) else []


def fetch_filing_data(ein: str) -> list:
    """
    Fetch all available yearly data for one organization.
    """
    logging.info("Requesting data for EIN: %s from the official endpoint...", ein)
    endpoint = "irs-data/990basic120fields"
    params = {"ein": ein}

    try:
        request_url = requests.Request("GET", BASE_URL + endpoint, params=params).prepare().url
        logging.info("Executing Request URL: %s", request_url)

        response = build_session().get(BASE_URL + endpoint, params=params, timeout=30)
        response.raise_for_status()

        results = extract_results(response.json())
        if results:
            logging.info("Success! Received %s records for EIN %s.", len(results), ein)
            return results

        logging.warning("API returned empty results for EIN: %s.", ein)
        return []

    except requests.exceptions.RequestException as exc:
        logging.error("Network error while requesting data for EIN %s: %s", ein, exc)
        return []
    except json.JSONDecodeError:
        logging.error("Failed to decode the JSON response from the server.")
        return []


if __name__ == "__main__":
    print("====== Data Harvester FINAL: Based on Official Documentation ======")

    all_years_data = fetch_filing_data(TEST_EIN)

    if all_years_data:
        print(f"\n====== Successfully retrieved {len(all_years_data)} year(s) of data for EIN {TEST_EIN} ======")

        df = pd.DataFrame(all_years_data)
        display_columns = ["TAXYEAR", "FILERNAME1", "TOTREVCURYEA", "TOTEXPCURYEA", "NAFBEOY"]
        existing_columns = [col for col in display_columns if col in df.columns]

        if existing_columns:
            print(df[existing_columns].to_string(index=False))
        else:
            print("Results returned, but expected display columns were not present.")

        print("\n======================================================================\n")
        print("SUCCESS: Retrieved and displayed data from the official endpoint.")
    else:
        print("No records were returned for this EIN.")
