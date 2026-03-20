import json
import logging

import pandas as pd
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = "https://990-infrastructure.gtdata.org/"
TEST_EIN = "530196605"


def build_session() -> requests.Session:
    session = requests.Session()
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


def get_data_with_official_dictionary(ein: str):
    """
    Fetch and process data using official field names from the data dictionary.
    """
    logging.info("Requesting data for EIN: %s...", ein)
    endpoint = "irs-data/990basic120fields"
    params = {"ein": ein}
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )
    }

    try:
        request_url = requests.Request("GET", BASE_URL + endpoint, params=params).prepare().url
        logging.info("Executing Request URL: %s", request_url)

        response = build_session().get(BASE_URL + endpoint, params=params, headers=headers, timeout=30)
        response.raise_for_status()

        results_list = extract_results(response.json())
        if results_list:
            logging.info("SUCCESS! Found %s records in the API response.", len(results_list))
            return results_list

        logging.error("API call succeeded, but no records were found in body.results.")
        return []

    except requests.exceptions.RequestException as exc:
        logging.error("A network error occurred: %s", exc)
        return []
    except json.JSONDecodeError:
        logging.error("Failed to decode the JSON response from the server.")
        return []


if __name__ == "__main__":
    print("====== Data Harvester FINAL: Official Data Dictionary Edition ======")

    all_years_data = get_data_with_official_dictionary(TEST_EIN)

    if all_years_data:
        df = pd.DataFrame(all_years_data)

        column_mapping = {
            "TAXYEAR": "tax_year",
            "FILERNAME1": "organization_name",
            "TOTREVCURYEA": "total_revenue",
            "TOTEXPCURYEA": "total_expenses",
            "NAFBEOY": "net_assets",
        }

        existing_source_cols = [c for c in column_mapping.keys() if c in df.columns]
        display_df = df[existing_source_cols].rename(columns={k: column_mapping[k] for k in existing_source_cols})

        print(f"\n====== Successfully Extracted and Decoded {len(display_df)} Records ======")
        print(display_df.to_string(index=False))

        print("\n======================================================================\n")
        print("SUCCESS: Data was extracted and displayed using official dictionary fields.")
    else:
        print("No records returned for the requested EIN.")