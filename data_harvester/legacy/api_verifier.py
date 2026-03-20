import json
import logging

import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = "https://990-infrastructure.gtdata.org/"
TEST_EIN = "842929872"


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


def request_endpoint(endpoint: str, ein: str) -> list:
    params = {"ein": ein}
    response = build_session().get(BASE_URL + endpoint, params=params, timeout=30)
    response.raise_for_status()
    return extract_results(response.json())


def final_verify_api() -> bool:
    try:
        logging.info(">>> Testing 'efilexml' endpoint for EIN: %s ...", TEST_EIN)
        xml_results = request_endpoint("irs-data/efilexml", TEST_EIN)

        print("\n--- efilexml summary ---")
        if xml_results:
            latest = xml_results[0]
            print(f"Found {len(xml_results)} filing records.")
            print(f"Latest ObjectId: {latest.get('ObjectId')}")
            print(f"Organization: {latest.get('OrganizationName')}")
        else:
            print("No efilexml records returned.")
        print("------------------------\n")

        logging.info(">>> Testing '990basic120fields' endpoint for EIN: %s ...", TEST_EIN)
        basic_results = request_endpoint("irs-data/990basic120fields", TEST_EIN)

        print("--- 990basic120fields summary ---")
        if basic_results:
            latest = basic_results[0]
            print(f"Found {len(basic_results)} parsed records.")
            print(f"Organization: {latest.get('FILERNAME1')}")
            print(f"Tax year: {latest.get('TAXYEAR')}")
            print(f"Total revenue: {latest.get('TOTREVCURYEA')}")
            print("---------------------------------\n")
            return True

        print("No parsed records returned.")
        print("---------------------------------\n")
        return False

    except requests.exceptions.RequestException as exc:
        logging.error("Network error during API verification: %s", exc)
        return False
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON response.")
        return False


if __name__ == "__main__":
    print("====== Giving Tuesday API Verifier (V9) ======")
    success = final_verify_api()
    print("\n====== Verification Complete ======")
    if success:
        print("SUCCESS: Official API endpoints are reachable and returning data.")
    else:
        print("FAILED: API check did not return expected data.")