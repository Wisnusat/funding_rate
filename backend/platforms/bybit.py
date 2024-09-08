import ccxt
import time
import json
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.utils import time_converter
from app.logger import logger
from app.db.models import BybitDB
from app.db.operations import save_to_database

class Bybit:
    @staticmethod
    def run(interval='1h'):
        """
        Run the Bybit scraper process for the given interval.

        This method orchestrates the scraping of Bybit data, processing it, and saving it to the database.

        Args:
            interval (str): The interval at which the scraper will run. Defaults to '1h'.

        Returns:
            None
        """
        bybit_assets = Bybit.fetch_bybit_instrument_names()
        logger.info(f"[BYBIT] Running scraper for {interval} interval with assets: {len(bybit_assets)}")

        start_time = time.time()

        bybit_data = Bybit.runWithThreading(Bybit.fetch_bybit_data, interval, bybit_assets)
        processed_data = Bybit.process_bybit_data(bybit_data)

        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"[BYBIT] Data scraping completed in {duration:.2f} seconds.")

        save_status = save_to_database(processed_data, BybitDB)
        if save_status == True:
            logger.info(f"[BYBIT]Data saved to the database successfully.")
        else:
            logger.error(f"[BYBIT]{save_status}")

    @staticmethod
    def process_bybit_data(data):
        """
        Process raw Bybit data into a structured format.

        Args:
            data (list): A list of raw data fetched from Bybit.

        Returns:
            list: A list of processed data entries.
        """
        processed_data = []
        for entry in data:
            coin_symbol = entry['symbol'].split('/')[0]
            processed_entry = [
                coin_symbol,
                entry['timestamp'],
                entry['fundingRate'],
                None
            ]
            processed_data.append(processed_entry)
        return processed_data

    @staticmethod
    def fetch_bybit_instrument_names():
        """
        Fetch the list of instrument names from Bybit.

        This method retrieves all market pairs containing 'USDT' from Bybit's API.

        Returns:
            list: A list of instrument names that contain 'USDT'.
        """
        # exchange = ccxt.bybit()
        # exchange.load_markets()
        # return [pair for pair in exchange.markets if 'USDT' in pair]

        with open("data_const/avail_bybit.json", 'r', encoding='utf-8') as f:
            instrument_names = json.load(f)
        return instrument_names
        
    
    @staticmethod
    def fetch_bybit_data(symbol, since):
        """
        Fetch funding rate history data from Bybit for a given symbol.

        This method fetches funding rate history for a symbol starting from a given timestamp.

        Args:
            symbol (str): The trading symbol to fetch the funding rate history for.
            since (int): The timestamp from which to start fetching the data.

        Returns:
            list: A list of funding rate history data.
        """
        exchange = ccxt.bybit()
        all_data = []
        since = time_converter(since)

        while True:
            try:
                data = exchange.fetch_funding_rate_history(f'{symbol}/USDT:USDT', since, limit=200)
                if not data:
                    break
                all_data.extend(data)
                since = data[-1]['timestamp'] + 1
                if since >= int(datetime.now(timezone.utc).timestamp() * 1000):
                    break
            except Exception as e:
                # logger.error(f"Error fetching data for {symbol}: {e}")
                break

        return all_data

    @staticmethod
    def runWithThreading(fetch_data_function, since, instrument_names):
        """
        Run data fetching for multiple instruments concurrently using threading.

        Args:
            fetch_data_function (function): The function used to fetch data.
            since (int): The starting timestamp for fetching data.
            instrument_names (list): A list of instrument names to fetch data for.

        Returns:
            list: Combined results from all threads.
        """
        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(fetch_data_function, instrument_name, since)
                for instrument_name in instrument_names
            ]
            for future in as_completed(futures):
                data = future.result()
                if data:
                    results.extend(data)

        return results
