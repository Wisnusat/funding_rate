import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from fake_useragent import UserAgent
from app.db.models import HyperliquidDB
from app.db.operations import save_to_database, delete_all_data, count_rows
from app.utils import get_timeframe
from app.logger import logger
import gc
from app.config import Config
class Hyperliquid:
    @staticmethod
    def run(interval='1h'):
        """
        Run the Hyperliquid scraper for the given interval with memory optimization.

        This method fetches instrument names, scrapes data for those instruments using threading, processes the data, and saves it to the database.

        Args:
            interval (str): The interval at which to run the scraper, e.g., '1h', '1d'.

        Returns:
            None
        """
        hyperliquid_assets = Hyperliquid.fetch_hyperliquid_instrument_name()
        logger.info(f"[HYPER]Running scraper for {interval} interval with assets: {len(hyperliquid_assets)}")

        # Start timing
        start_time = time.time()

        # Process assets in smaller batches to avoid memory overload
        batch_size = Config.BATCH_SIZE
        batch_iteration = 0
        for i in range(0, len(hyperliquid_assets), batch_size):
            batch_assets = hyperliquid_assets[i:i + batch_size]
            hyperliquid_data = Hyperliquid.run_with_threading(Hyperliquid.fetch_hyperliquid_data, interval, batch_assets)

            # Process data to match the expected format
            processed_data = Hyperliquid.process_hyperliquid_data(hyperliquid_data)

            # Save processed data to the database
            save_status = save_to_database(processed_data, HyperliquidDB)
            batch_iteration += 1
            if save_status == True:
                logger.info(f"[HYPER][{batch_iteration}] Data batch saved successfully.")
            else:
                logger.error(f"[HYPER][{batch_iteration}] {save_status}")

            # Free memory after processing each batch
            gc.collect()

        # End timing
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"[HYPER] Data scraping completed in {duration:.2f} seconds.")

    @staticmethod
    def fetch_hyperliquid_instrument_name():
        """
        Fetch instrument names from the Hyperliquid API.

        This method retrieves instrument names from the Hyperliquid API by making a POST request.

        Returns:
            list: A list of instrument names fetched from the Hyperliquid API.
        """
        # ua = UserAgent()
        # url = 'https://api.hyperliquid.xyz/info'
        # headers = {
        #     'Content-Type': 'application/json',
        #     'User-Agent': ua.random
        # }
        # payload = {
        #     'type': 'meta'
        # }

        try:
            # response = requests.post(url, headers=headers, json=payload)
            # response.raise_for_status()  # Raise HTTPError for bad responses
            # data = response.json()

            # instrument_names = [instrument['name'] for instrument in data['universe']]

            with open("data_const/avail_hyper.json", 'r', encoding='utf-8') as f:
                instrument_names = json.load(f)
            return instrument_names

        except requests.RequestException as e:
            logger.info(f"[HYPER]An error occurred while fetching metadata: {e}")
            return []

    @staticmethod
    def process_hyperliquid_data(data):
        """
        Process raw Hyperliquid data into a structured format.

        Args:
            data (list): A list of raw data entries fetched from Hyperliquid.

        Returns:
            list: A list of processed data entries.
        """
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
    def fetch_hyperliquid_data(symbol, start_time, end_time, limit=500):
        """
        Fetch funding rate history data from Hyperliquid for a given symbol.

        This method fetches funding rate history for a given symbol by making an API call. It retries up to a set limit in case of errors.

        Args:
            symbol (str): The name of the instrument to fetch funding data for.
            start_time (int): The start timestamp for fetching data.
            end_time (int): The end timestamp for fetching data.
            limit (int, optional): The maximum number of data points to retrieve per request. Defaults to 500.

        Returns:
            list: A list of funding history data fetched from the Hyperliquid API.
        """
        session = requests.Session()  # Reuse session for all requests
        ua = UserAgent()
        url = 'https://api.hyperliquid.xyz/info'
        all_data = []
        current_start_time = start_time

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
                    response = session.post(url, headers=headers, json=payload)
                    response.raise_for_status()  # Raise HTTPError for bad responses
                    data = response.json()

                    if not data:
                        return all_data

                    all_data.extend(data)

                    if len(data) < limit:
                        return all_data

                    current_start_time = data[-1]['time']
                    break  # Break out of the retry loop if successful

                except requests.RequestException as e:
                    req_failed += 1
                    retries += 1
                    if retries >= max_retries:
                        return all_data  # Return what we have so far if retries are exhausted
                    wait_time = backoff_factor ** retries
                    time.sleep(wait_time)
        
        if req_failed:
            logger.error(f"[HYPER] {req_failed} requests failed")

        return all_data

    @staticmethod
    def run_with_threading(fetch_data_function, interval, instrument_names):
        """
        Run data fetching for multiple instruments concurrently using threading.

        This method fetches data for multiple instruments in parallel using threads.

        Args:
            fetch_data_function (function): The function used to fetch data.
            interval (str): The interval for the data fetch operation.
            instrument_names (list): A list of instrument names to fetch data for.

        Returns:
            list: Combined results from all threads.
        """
        start_time, end_time = get_timeframe(interval)

        results = []
        max_workers = min(10, len(instrument_names))  # Dynamically adjust the number of workers
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(fetch_data_function, instrument_name, start_time, end_time)
                for instrument_name in instrument_names
            ]
            for future in as_completed(futures):
                data = future.result()
                if data:
                    results.extend(data)

        return results
