import ccxt
import requests
import time, datetime
import logging
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.db.models import BybitDB
from app.db.operations import save_to_database, delete_all_data, count_rows
from app.utils import get_timeframe

# use ccxt library to get data from bybit
class Bybit:
    @staticmethod
    def run(interval='1h'):
        bybit_assets = Bybit.fetch_bybit_instrument_names()
        # bybit_assets = ["BTC"]
        print(f"[BYBIT]Running scraper for {interval} interval with assets: {len(bybit_assets)}")
        
        # Start timing
        start_time = time.time()
        
        # Scrape data from Bybit
        bybit_data = Bybit.runWithThreading(Bybit.fetch_bybit_data, interval, bybit_assets)

        # Process data to match the expected format
        processed_data = Bybit.process_bybit_data(bybit_data)

        # End timing
        end_time = time.time()
        duration = end_time - start_time

        # Display duration
        print(f"[BYBIT]Data scraping completed in {duration:.2f} seconds.")

        # Save to database
        save_to_database(processed_data, BybitDB)

    def process_bybit_data(data):
        processed_data = []
        for entry in data:
            coin_symbol = entry['symbol'].replace('USDT', '')
            processed_entry = [
                coin_symbol,
                int(entry['fundingRateTimestamp']),
                entry['fundingRate'],
                None
            ]
            processed_data.append(processed_entry)
        return processed_data

    # delete all data from the database
    @staticmethod
    def delete_all_data():
        delete_all_data(BybitDB)

    # count the number of rows in the database
    @staticmethod
    def count_rows():
        count = count_rows(BybitDB)
        print(f"[BYBIT]Number of rows in the database: {count}")

    # Fetch instrument names from Bybit
    def fetch_bybit_instrument_names():
        url = "https://api.bybit.com/v2/public/symbols"
        headers = {
            'accept': 'application/json'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            # Extract the list of instruments from the 'result' key
            instruments = response.json()['result']

            # Extract base_currency from each instrument
            instrument_names = [instrument['base_currency'] for instrument in instruments]
            return instrument_names

        except requests.RequestException as e:
            print(f"[BYBIT]An error occurred while fetching instrument names: {e}")
            return []
    
    # https://bybit-exchange.github.io/docs/api-explorer/v5/market/history-fund-rate
    def fetch_bybit_data(symbol, start_time, end_time, limit=200):
        url = 'https://api.bybit.com/derivatives/v3/public/funding/history-funding-rate'
        headers = {
            'accept': 'application/json'
        }
        
        all_data = []
        current_end_time = end_time
        loop = 1

        while current_end_time > start_time:
            params = {
                'symbol': symbol.upper() + "USDT",
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

                    if data['retCode'] != 0:
                        error_message = data.get('retMsg', 'Unknown error')
                        print(f"[BYBIT][{retries}]Error fetching {symbol} data: {error_message}")
                        
                        # Break the loop if it's an invalid symbol error or retries have been exhausted
                        if 'Symbol Invalid' in error_message or retries >= max_retries:
                            return []  # Return an empty list or handle the error accordingly
                        
                        retries += 1
                        wait_time = backoff_factor ** retries
                        time.sleep(wait_time)
                        continue

                    # print(f"[BYBIT]Data fetched for {symbol}")
                    loop += 1
                    all_data.extend(data['result']['list'])

                    if len(data['result']['list']) < limit:
                        # If less data than the limit was returned, we've reached the earliest data available
                        return all_data

                    # Update the current_end_time to the timestamp of the earliest data point retrieved
                    current_end_time = min(int(item['fundingRateTimestamp']) for item in data['result']['list'])
                    break  # Break out of the retry loop if successful
                except requests.RequestException as e:
                    print(f"[BYBIT]Request failed: {e}")
                    retries += 1
                    if retries >= max_retries:
                        return []  # Break out of the loop after max retries and return an empty list
                    wait_time = backoff_factor ** retries
                    time.sleep(wait_time)

        return all_data



    # Run with threading to fetch data for multiple instruments
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

    