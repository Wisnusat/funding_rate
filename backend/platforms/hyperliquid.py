import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from fake_useragent import UserAgent
from app.db.models import HyperliquidDB
from app.db.operations import save_to_database, delete_all_data, count_rows
from app.utils import get_timeframe
from app.logger import logger

class Hyperliquid:
    @staticmethod
    def run(interval='1h'):
        """
        Run the Hyperliquid scraper for the given interval.

        This method fetches instrument names, scrapes data for those instruments using threading, processes the data, and saves it to the database.

        Args:
            interval (str): The interval at which to run the scraper, e.g., '1h', '1d'.

        Returns:
            None
        """
        hyperliquid_assets = Hyperliquid.fetch_hyperliquid_instrument_name()
        hyperliquid_assets = hyperliquid_assets[:5]
        logger.info(f"[HYPER]Running scraper for {interval} interval with assets: {len(hyperliquid_assets)}")

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
        logger.info(f"[HYPER]Data scraping completed in {duration:.2f} seconds.")

        # Save to database
        save_status = save_to_database(processed_data, HyperliquidDB)
        if save_status == True:
            logger.info(f"[HYPER]Data saved to the database successfully.")
        else:
            logger.error(f"[HYPER]{save_status}")

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
    def delete_all_data():
        """
        Delete all data from the Hyperliquid database.

        This method deletes all rows in the HyperliquidDB table.

        Returns:
            None
        """
        delete_all_data(HyperliquidDB)

    @staticmethod
    def count_rows():
        """
        Count the number of rows in the Hyperliquid database.

        This method counts and logger.infos the number of rows in the HyperliquidDB table.

        Returns:
            None
        """
        count = count_rows(HyperliquidDB)
        logger.info(f"[HYPER]Number of rows in the database: {count}")

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
                    response = requests.post(url, headers=headers, json=payload)
                    response.raise_for_status()  # Raise HTTPError for bad responses
                    data = response.json()

                    if not data:
                        # logger.warning(f"[HYPER]No data returned for {symbol}.")
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
                        # logger.info("Max retries reached. Returning what we have so far.")
                        return all_data  # Return what we have so far if retries are exhausted
                    wait_time = backoff_factor ** retries
                    time.sleep(wait_time)
        
        if req_failed:
           logger.error(f"[HYPER]{req_failed} Request failed")
        
        return all_data

    @staticmethod
    def runWithThreading(fetch_data_function, interval, instrument_names):
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
