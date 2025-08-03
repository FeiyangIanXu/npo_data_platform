import requests
import json
import logging
import pandas as pd

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = "https://990-infrastructure.gtdata.org/"
TEST_EIN = "000065837" # Giving Tuesday's EIN, as used in their sample request

def fetch_filing_data(ein: str) -> list:
    """
    Fetches all available yearly data for a single organization based on the official API documentation.
    """
    logging.info(f"Requesting data for EIN: {ein} from the official endpoint...")
    endpoint = "irs-data/990basic120fields"
    
    # We follow the documentation precisely: only the 'ein' parameter is sent.
    params = {'ein': ein}
    
    try:
        # Prepare the full request URL for logging, so we know exactly what we are asking for
        request_url = requests.Request('GET', BASE_URL + endpoint, params=params).prepare().url
        logging.info(f"Executing Request URL: {request_url}")

        response = requests.get(BASE_URL + endpoint, params=params, timeout=30)
        response.raise_for_status()  # This will raise an error for statuses like 404 or 500
        
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            logging.info(f"Success! Received {len(data)} records for EIN {ein}.")
            return data # Return the entire list of yearly filings
        else:
            logging.warning(f"API returned an empty list or invalid data for EIN: {ein}.")
            return None
            
    except requests.exceptions.RequestException as e:
        logging.error(f"A network error occurred while requesting data for EIN {ein}: {e}")
        return None
    except json.JSONDecodeError:
        logging.error("Failed to decode the JSON response from the server.")
        return None

if __name__ == "__main__":
    print("====== Data Harvester FINAL: Based on Official Documentation ======")
    
    # 1. Fetch the data according to the manual
    all_years_data = fetch_filing_data(TEST_EIN)
    
    if all_years_data:
        # 2. Display the results clearly
        print(f"\n====== Successfully retrieved {len(all_years_data)} year(s) of data for EIN {TEST_EIN} ======")
        
        # We can use pandas to display this list of dictionaries beautifully
        df = pd.DataFrame(all_years_data)
        
        # Select and reorder a few key columns for a clean display
        display_columns = [
            'tax_year', 'organization_name', 'total_revenue', 
            'total_expenses', 'net_assets'
        ]
        
        # Filter the DataFrame to only show columns that actually exist in the response
        existing_columns = [col for col in display_columns if col in df.columns]
        
        print(df[existing_columns].to_string(index=False))
        
        print("\n======================================================================\n")
        print("🏆🏆🏆 VICTORY! By strictly following the official documentation, we have successfully retrieved the data.")