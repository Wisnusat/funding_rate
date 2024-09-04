import ccxt
import pandas as pd
from datetime import datetime, timezone, timedelta
import time
from sqlalchemy import create_engine
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.utils import get_timeframe, time_converter
from app.db.models import BybitDB
from app.db.operations import save_to_database, delete_all_data, count_rows

class Bybit:
    @staticmethod
    def run(interval='1h'):
        bybit_assets = Bybit.fetch_bybit_instrument_names()
        # bybit_assets = ['BTC/USDT:USDT', 'ETH/USDT:USDT']
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

    @staticmethod
    def process_bybit_data(data):
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
        exchange = ccxt.bybit()
        exchange.load_markets()
        # Return list of symbols that contain 'USDT'
        return [pair for pair in exchange.markets if 'USDT' in pair]
    
    @staticmethod
    def fetch_bybit_data(symbol, since):
        exchange = ccxt.bybit()
        all_data = []
        since = time_converter(since)  # Convert to milliseconds
        
        while True:
            try:
                data = exchange.fetch_funding_rate_history(f'{symbol}:USDT', since, limit=200)
                if not data:
                    break
                all_data.extend(data)
                since = data[-1]['timestamp'] + 1  # Move to the next timestamp
                # print(f"[BYBIT][{symbol}]: Fetched {len(data)} entries")
                # If we reached the end_time, stop the loop
                if since >= int(datetime.now(timezone.utc).timestamp() * 1000):
                    break
            except Exception as e:
                # print(f"[BYBIT][{symbol}]: {e}")
                break

        return all_data

    @staticmethod
    def runWithThreading(fetch_data_function, since, instrument_names):
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
