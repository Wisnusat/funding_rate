import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from fake_useragent import UserAgent
from app.db.models import HyperliquidDB
from app.db.operations import save_to_database, delete_all_data, count_rows
from app.utils import get_timeframe

class Hyperliquid:
    @staticmethod
    def run(interval='1h'):
        hyperliquid_assets = Hyperliquid.fetch_hyperliquid_instrument_name()
        print(f"[Hyperliquid]Running scraper for {interval} interval with assets: {len(hyperliquid_assets)}")

        # Start timing
        start_time = time.time()

        # Fetch and process data from Hyperliquid
        hyperliquid_data = Hyperliquid.runWithThreading(Hyperliquid.fetch_hyperliquid_data, interval, hyperliquid_assets)
        
        # Process data to match the expected format
        processed_data = Hyperliquid.process_hyperliquid_data(hyperliquid_data)

        # End timing
        end_time = time.time()
        duration = end_time - start_time

        # Display duration
        print(f"[Hyperliquid]Data scraping completed in {duration:.2f} seconds.")

        # Save to database
        save_to_database(processed_data, HyperliquidDB)

    @staticmethod
    def fetch_hyperliquid_instrument_name():
        ua = UserAgent()
        url = 'https://api.hyperliquid.xyz/info'
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': ua.random
        }
        payload = {
            'type': 'meta'
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()  # Raise HTTPError for bad responses
            data = response.json()

            instrument_names = [instrument['name'] for instrument in data['universe']]
            return instrument_names

        except requests.RequestException as e:
            print(f"[Hyperliquid]An error occurred while fetching metadata: {e}")
            return []

    @staticmethod
    def process_hyperliquid_data(data):
        processed_data = []
        for entry in data:
            processed_entry = [                
                entry.get('coin'),
                entry.get('time'),
                entry.get('fundingRate'),
                None
            ]
            processed_data.append(processed_entry)
        return processed_data

    @staticmethod
    def delete_all_data():
        delete_all_data(HyperliquidDB)

    @staticmethod
    def count_rows():
        count = count_rows(HyperliquidDB)
        print(f"[Hyperliquid]Number of rows in the database: {count}")

    @staticmethod
    def fetch_hyperliquid_data(symbol, start_time, end_time, limit=500):
        ua = UserAgent()
        url = 'https://api.hyperliquid.xyz/info'
        all_data = []
        current_start_time = start_time
        loop = 1

        req_failed = 0

        while current_start_time < end_time:
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': ua.random
            }
            payload = {
                'type': 'fundingHistory',
                'coin': symbol.upper(),
                'startTime': current_start_time,
                'endTime': end_time,
                'limit': limit  # Ensure the limit is applied
            }
            
            retries = 0
            max_retries = 2
            backoff_factor = 10  # Exponential backoff factor

            while retries < max_retries:
                try:
                    response = requests.post(url, headers=headers, json=payload)
                    response.raise_for_status()  # Raise HTTPError for bad responses
                    data = response.json()

                    if not data:
                        print(f"[Hyperliquid]No data returned for {symbol}.")
                        return all_data

                    loop += 1
                    all_data.extend(data)

                    if len(data) < limit:
                        return all_data

                    current_start_time = data[-1]['time']

                    break  # Break out of the retry loop if successful

                except requests.RequestException as e:
                    req_failed += 1
                    retries += 1
                    if retries >= max_retries:
                        # print("Max retries reached. Returning what we have so far.")
                        return all_data  # Return what we have so far if retries are exhausted
                    wait_time = backoff_factor ** retries
                    time.sleep(wait_time)
        
        if req_failed:
           print(f"[Hyperliquid]{req_failed} Request failed")
        
        return all_data

    @staticmethod
    def runWithThreading(fetch_data_function, interval, instrument_names):
        start_time, end_time = get_timeframe(interval)

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
