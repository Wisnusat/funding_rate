import ccxt
import pandas as pd
from datetime import datetime, timezone, timedelta
import time
from sqlalchemy import create_engine
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.utils import get_timeframe, time_converter
from app.db.models import GateioDB
from app.db.operations import save_to_database, delete_all_data, count_rows

class Gateio:
    @staticmethod
    def run(interval='1h'):
        gateio_assets = Gateio.fetch_gateio_instrument_names()
        # gateio_assets = ['BTC/USDT:USDT', 'ETH/USDT:USDT']
        print(f"[GATE]Running scraper for {interval} interval with assets: {len(gateio_assets)}")
        
        # Start timing
        start_time = time.time()
        
        # Scrape data from Gateio
        gateio_data = Gateio.runWithThreading(Gateio.fetch_gateio_data, interval, gateio_assets)

        # Process data to match the expected format
        processed_data = Gateio.process_gateio_data(gateio_data)

        # End timing
        end_time = time.time()
        duration = end_time - start_time

        # Display duration
        print(f"[GATE]Data scraping completed in {duration:.2f} seconds.")

        # Save to database
        save_to_database(processed_data, GateioDB)

    @staticmethod
    def process_gateio_data(data):
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
        exchange = ccxt.gate()
        exchange.load_markets()
        # Return list of symbols that contain 'USDT'
        return [pair for pair in exchange.markets if 'USDT' in pair]
    
    @staticmethod
    def fetch_gateio_data(symbol, since):
        exchange = ccxt.gate()
        since = time_converter(since)
        data = []
        try:
            data = exchange.fetch_funding_rate_history(f'{symbol}:USDT', since, limit=1000)
        except Exception as e:
            # print(f"[GATE][{symbol}]: {e}")
            f"[Gate.io] Error fetching funding rate history"

        return data

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
