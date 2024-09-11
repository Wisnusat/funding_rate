import ccxt
import gc
import time
import json
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.utils import get_timeframe, time_converter
from app.logger import logger
from app.db.models import GateioDB
from app.db.operations import save_to_database, delete_all_data, count_rows

class Gateio:
    @staticmethod
    def run(interval='1h'):
        """
        Run the Gateio scraper process for the given interval with memory optimization.
        Processes data for each asset in batches and saves it to the database while 
        running garbage collection after each batch to free memory.

        Args:
            interval (str): The interval at which to run the scraper, e.g., '1h', '1d'.
        
        Returns:
            None
        """
        gateio_assets = Gateio.fetch_gateio_instrument_names()
        logger.info(f"[GATE]Running scraper for {interval} interval with assets: {len(gateio_assets)}")
        
        start_time = time.time()

        # Process data in smaller batches to avoid running out of memory
        batch_size = 50  # Process 50 assets at a time
        for i in range(0, len(gateio_assets), batch_size):
            batch_assets = gateio_assets[i:i + batch_size]
            gateio_data = Gateio.run_with_threading(Gateio.fetch_gateio_data, interval, batch_assets)
            processed_data = Gateio.process_gateio_data(gateio_data)
            
            # Save the batch to the database
            save_status = save_to_database(processed_data, GateioDB)
            if save_status == True:
                # Data saved successfully
                pass
            else:
                logger.error(f"[GATE]{save_status}")
            
            # Run garbage collection to free up memory after each batch
            gc.collect()
        
        logger.info(f"[GATE]Data saved to the database successfully.")

        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"[GATE]Data scraping completed in {duration:.2f} seconds.")

    @staticmethod
    def process_gateio_data(data):
        """
        Process raw Gate.io data into a structured format suitable for database storage.

        Args:
            data (list): A list of raw data entries fetched from Gate.io.

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
    def fetch_gateio_instrument_names():
        """
        Fetch the list of instrument names from Gate.io.

        Returns:
            list: A list of instrument names that include 'USDT'.
        """
        # exchange = ccxt.gate()
        # exchange.load_markets()
        # # Return list of symbols that contain 'USDT'
        # return [pair for pair in exchange.markets if 'USDT' in pair]
        
        with open("data_const/avail_gate.json", 'r', encoding='utf-8') as f:
            instrument_names = json.load(f)
        return instrument_names
    
    @staticmethod
    def fetch_gateio_data(symbol, since, limit=1000):
        """
        Fetch funding rate history data from Gate.io for a given symbol.

        Args:
            symbol (str): The symbol to fetch funding rate data for.
            since (int): The timestamp to start fetching data from.
            limit (int, optional): The number of records to fetch per request. Defaults to 1000.

        Returns:
            list: A list of funding rate history data for the given symbol.
        """
        exchange = ccxt.gate()
        since = time_converter(since)
        data = []
        try:
            data = exchange.fetch_funding_rate_history(f'{symbol}/USDT:USDT', since, limit=limit)
        except Exception as e:
            logger.error(f"[GATE][{symbol}]: {e}")
        return data

    @staticmethod
    def run_with_threading(fetch_data_function, since, instrument_names):
        """
        Run data fetching for multiple instruments concurrently with reduced memory usage.
        Optimized for batch processing and reduced memory usage by limiting the number of threads.

        Args:
            fetch_data_function (function): The function to fetch data.
            since (str): The starting timestamp for fetching data.
            instrument_names (list): List of instrument names to fetch data for.
        
        Returns:
            list: Combined results from all threads.
        """
        results = []
        max_workers = min(10, len(instrument_names))  # Dynamically adjust the number of workers
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(fetch_data_function, instrument_name, since)
                for instrument_name in instrument_names
            ]
            for future in as_completed(futures):
                data = future.result()
                if data:
                    results.extend(data)

        return results
