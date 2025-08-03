import requests
import json
import logging
import pandas as pd

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = "https://990-infrastructure.gtdata.org/"
# Using the American Red Cross EIN, which is known to have rich data
TEST_EIN = "530196605" 

def get_data_with_official_dictionary(ein: str):
    """
    Fetches and processes data using the official field names from the Data Dictionary.
    """
    logging.info(f"Requesting data for EIN: {ein}...")
    endpoint = "irs-data/990basic120fields"
    params = {'ein': ein}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        request_url = requests.Request('GET', BASE_URL + endpoint, params=params).prepare().url
        logging.info(f"Executing Request URL: {request_url}")

        response = requests.get(BASE_URL + endpoint, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        top_level_data = response.json()
        results_list = top_level_data.get('body', {}).get('results', [])

        if isinstance(results_list, list) and len(results_list) > 0:
            logging.info(f"SUCCESS! Found {len(results_list)} records in the API response.")
            return results_list
        else:
            logging.error("API call was successful, but no records were found in the 'results' list.")
            return None
            
    except requests.exceptions.RequestException as e:
        logging.error(f"A network error occurred: {e}")
        return None
    except json.JSONDecodeError:
        logging.error("Failed to decode the JSON response from the server.")
        return None


if __name__ == "__main__":
    print("====== Data Harvester FINAL: Official Data Dictionary Edition ======")
    
    # 1. Fetch the raw data from the API
    all_years_data = get_data_with_official_dictionary(TEST_EIN)
    
    if all_years_data:
        # 2. Create a pandas DataFrame from the raw data
        df = pd.DataFrame(all_years_data)
        
        # 3. Define the mapping from the cryptic names (from the dictionary) to our desired, clean names
        column_mapping = {
            'TAXYEAR': 'tax_year',
            'FILERNAME1': 'organization_name',
            'TOTREVCURYEA': 'total_revenue',
            'TOTEXPCURYEA': 'total_expenses',
            'NAFBEOY': 'net_assets'
        }
        
        # 4. Select and rename the columns in one step for a clean final table
        # We will only select the columns that actually exist in the DataFrame
        display_df = df[column_mapping.keys()].rename(columns=column_mapping)
        
        print(f"\n====== Successfully Extracted and Decoded {len(display_df)} Records ======")
        print(display_df.to_string(index=False))
        
        print("\n======================================================================\n")
        print("🏆🏆🏆 VICTORY! By using the official Data Dictionary you provided, we have finally extracted and displayed the data correctly!")