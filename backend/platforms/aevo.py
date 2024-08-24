import requests
import time, datetime
from app.db.models import AevoDB
from app.utils import get_timestamp_for_interval
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.db.operations import save_to_database, delete_all_data, count_rows

class Aevo:
    @staticmethod
    def run(interval='1h'):
        aevo_assets = Aevo.fetch_aevo_instrument_names()
        aevo = Aevo()
        print(f"[AEVO]Running scraper for {interval} interval with assets: {len(aevo_assets)}")
        
        # Start timing
        start_time = time.time()
        
        # Scrape data from AEVO
        aevo_data = Aevo.runWithThreading(Aevo.fetch_aevo_data, interval, aevo_assets)
        
        # Process data to match the expected format
        processed_aevo_data = Aevo.process_aevo_data(aevo_data)

        # End timing
        end_time = time.time()
        duration = end_time - start_time
        
        # Display duration
        print(f"[AEVO]Data scraping completed in {duration:.2f} seconds.")
        
        save_to_database(processed_aevo_data, AevoDB)
    
    def process_aevo_data(data):
        processed_data = []
        for entry in data:
            coin_symbol = entry[0].replace('-PERP', '')
            processed_entry = [
                coin_symbol,
                int(entry[1]),
                entry[2],
                entry[3]
            ]
            processed_data.append(processed_entry)
        return processed_data

    # delete all data from the database
    @staticmethod
    def delete_all_data():
        delete_all_data(AevoDB)

    # count the number of rows in the database
    @staticmethod
    def count_rows():
        count = count_rows(AevoDB)
        print(f"[AEVO]Number of rows in the database: {count}")

    # Fetch instrument names from AEVO
    def fetch_aevo_instrument_names():
        url = "https://api.aevo.xyz/assets"
        headers = {
            'accept': 'application/json'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            instrument_names = response.json()
            return instrument_names

        except requests.RequestException as e:
            print(f"[AEVO]An error occurred while fetching instrument names: {e}")
            return []

    def fetch_aevo_data(instrument_name, start_time, end_time, limit=50):
        url = 'https://api.aevo.xyz/funding-history'
        headers = {
            'accept': 'application/json'
        }
        
        all_data = []
        current_end_time = end_time
        loop = 1

        while current_end_time > start_time:
            params = {
                'instrument_name': f"{instrument_name.upper()}-PERP",
                'start_time': str(int(start_time)),
                'end_time': str(int(current_end_time)),
                'limit': limit
            }
            
            retries = 0
            max_retries = 2
            backoff_factor = 1.5  # Exponential backoff factor

            while retries < max_retries:
                try:
                    response = requests.get(url, params=params, headers=headers)
                    response.raise_for_status()  # Raise HTTPError for bad responses
                    data = response.json()
                    

                    if 'error' in data and data['error'] == 'RATE_LIMIT_EXCEEDED':
                        retry_after = int(data.get('retry_after', '0'))
                        wait_time = retry_after / 1e9  # Convert from nanoseconds to seconds
                        time.sleep(wait_time)
                        retries += 1
                    else:
                        # print(f"[AEVO]Data fetched for {instrument_name}")
                        all_data.extend(data['funding_history'])
                        loop += 1
                        if len(data['funding_history']) < limit:
                            # If less data than the limit was returned, we've reached the earliest data available
                            return all_data

                        # Update the current_end_time to the timestamp of the earliest data point retrieved
                        current_end_time = min(int(item[1]) for item in data['funding_history'])
                        break
                except requests.RequestException as e:
                    retries += 1
                    wait_time = backoff_factor ** retries
                    time.sleep(wait_time)
        
        return all_data

    # Run with threading to fetch data for multiple instruments
    def runWithThreading(fetch_data_function, interval, instrument_names):
        start_time, end_time = get_timestamp_for_interval(interval)
        
        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(fetch_data_function, instrument_name, start_time, end_time)
                for instrument_name in instrument_names
            ]
            for future in as_completed(futures):
                data = future.result()
                if data:
                    results.extend(data)

        return results
    
