import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from db.models import GateioDB  # Adjusted to reflect the correct database model for Gate.io data
from db.operations import save_to_database, delete_all_data, count_rows, get_data_by_params
from utils.common import get_timeframe

class Gateio:
    @staticmethod
    def run(limit=1):
        gateio_assets = Gateio.fetch_gateio_instrument_name()
        # gateio_assets = ["btc"]
        print(f"Running Gateio scraper for {interval} interval with assets: {len(gateio_assets)}")

        # Start timing
        start_time = time.time()

        # Fetch and process data from Gateio
        gateio_data = Gateio.runWithThreading(Gateio.fetch_gateio_data, interval, gateio_assets, limit)
        
        # Process data to match the expected format
        processed_data = Gateio.process_gateio_data(gateio_data)

        # End timing
        end_time = time.time()
        duration = end_time - start_time

        # Display duration
        print(f"Data scraping completed in {duration:.2f} seconds.")

        # Save to database
        save_to_database(processed_data, GateioDB)

    @staticmethod
    def fetch_gateio_instrument_name():
        url = 'https://api.gateio.ws/api/v4/spot/currency_pairs'
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise HTTPError for bad responses
            data = response.json()
            
            instrument_names = [instrument['base'] for instrument in data]
            return instrument_names

        except requests.RequestException as e:
            print(f"An error occurred while fetching instrument names: {e}")
            return []

    @staticmethod
    def process_gateio_data(data):
        processed_data = []
        for entry in data:
            processed_entry = [                
                entry.get('symbol'),
                entry.get('t'),
                entry.get('r'),
                None  # Placeholder for additional data or calculations if needed
            ]
            processed_data.append(processed_entry)
        return processed_data

    # Delete all data from the database
    @staticmethod
    def delete_all_data():
        delete_all_data(GateioDB)

    # Count the number of rows in the database
    @staticmethod
    def count_rows():
        count = count_rows(GateioDB)
        print(f"Number of rows in the database: {count}")

    @staticmethod
    def get_data_by_params(instrument_name):
        data = get_data_by_params(GateioDB, instrument_name)
        return data

    @staticmethod
    def fetch_gateio_data(symbol, limit=1):
        url = 'https://api.gateio.ws/api/v4/futures/usdt/funding_rate'
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        params = {
            'contract': symbol.upper() + "_USDT",
            'limit': limit
        }
        
        retries = 0
        max_retries = 2
        backoff_factor = 1.5  # Exponential backoff factor

        while retries < max_retries:
            try:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()  # Raise HTTPError for bad responses
                data = response.json()

                if not data:
                    print(f"No data returned for {symbol}.")
                    return []

                # Add the symbol to each entry in the returned data
                for entry in data:
                    entry['symbol'] = symbol.upper()

                # print(f"[GATEIO]Data fetched for {symbol}")
                return data

            except requests.exceptions.HTTPError as e:
                if response.status_code == 400:
                    # print(f"Bad Request (400) for symbol: {symbol}. Skipping this symbol.")
                    return []  # Skip this symbol entirely
                else:
                    print(f"Request failed: {e}")
                    retries += 1
                    if retries >= max_retries:
                        print("Max retries reached. Returning what we have so far.")
                        return []  # Return what we have so far if retries are exhausted
                    wait_time = backoff_factor ** retries
                    time.sleep(wait_time)

            except requests.RequestException as e:
                print(f"Request failed: {e}")
                retries += 1
                if retries >= max_retries:
                    print("Max retries reached. Returning what we have so far.")
                    return []  # Return what we have so far if retries are exhausted
                wait_time = backoff_factor ** retries
                time.sleep(wait_time)

        return []


    @staticmethod
    def runWithThreading(fetch_data_function, interval, instrument_names, limit):
        start_time, end_time = get_timeframe(interval)

        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(fetch_data_function, instrument_name, limit)
                for instrument_name in instrument_names
            ]
            for future in as_completed(futures):
                data = future.result()
                if data:
                    results.extend(data)

        return results
