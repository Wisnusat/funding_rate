import requests
from datetime import datetime, timedelta, timezone
from app.utils import load_tickers, get_logo_url
from concurrent.futures import ThreadPoolExecutor
import logging

# Configure logging
logging.basicConfig(level=logging.WARNING)

class Aevo:
    @staticmethod
    def fetch_all_funding_history(page, limit, time, sort_order, keyword):
        ticker_aevo = load_tickers()

        # If a keyword is provided, filter the list of tickers
        if keyword:
            keyword_lower = keyword.lower()
            ticker_aevo = [ticker for ticker in ticker_aevo if keyword_lower in ticker.lower()]

        # Sort the ticker_aevo list
        ticker_aevo.sort(reverse=(sort_order == 'desc'))

        # Pagination
        total_items = len(ticker_aevo)
        res = {
            "meta": {
                "v_platform": "aevo",
                "v_endpoint": "https://api.aevo.xyz/funding-history",
                "v_docs": "https://api-docs.aevo.xyz/reference/getfundinghistory",
                "page": page,
                "perPage": limit,
                "totalPages": (total_items // limit) + (1 if total_items % limit != 0 else 0),
                "totalItems": total_items,
                "isNextPage": page * limit < total_items,
                "date": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z'),
            },
            "data": []
        }

        # Apply pagination to ticker_aevo
        ticker_aevo_paginated = ticker_aevo[(page - 1) * limit : page * limit]

        # Use ThreadPoolExecutor to fetch funding history concurrently
        with ThreadPoolExecutor() as executor:
            results = executor.map(lambda ticker: Aevo.process_ticker(ticker, time), ticker_aevo_paginated)

        # Collect results
        res['data'] = list(results)

        return res

    @staticmethod
    def process_ticker(ticker_name, time):
        ticker_name = f"{ticker_name}-PERP"
        funding_history = Aevo.fetch_single_funding_history(ticker_name, time)
        return str(funding_history[0]['rate']) if funding_history and 'rate' in funding_history[0] else "None"

    @staticmethod
    def fetch_single_funding_history(ticker, time):
        intervals = {
            '1h': timedelta(hours=1),
            '1d': timedelta(days=1),
            '7d': timedelta(days=7),
            '1M': timedelta(days=30),
            '1y': timedelta(days=365)
        }
        results = []
        current_time = datetime.now(timezone.utc)

        # Get interval by time parameter
        if time in intervals:
            intervals = {time: intervals[time]}

        for interval_name, interval_delta in intervals.items():
            end_time = current_time  # Each interval's end_time is now
            start_time = end_time - interval_delta
            chunk_size = interval_delta / (1 if interval_name == '1h' else 10)

            all_rates = []
            while start_time < end_time:
                chunk_end_time = min(start_time + chunk_size, end_time)
                start_time_ns = int(start_time.timestamp() * 1_000_000_000)
                chunk_end_time_ns = int(chunk_end_time.timestamp() * 1_000_000_000)

                # For '1h', set start_time_ns to 0
                if time == '1h' or time == '1d':
                    start_time_ns = 0

                response = requests.get(
                    'https://api.aevo.xyz/funding-history',
                    params={
                        'instrument_name': ticker,
                        'start_time': start_time_ns,
                        'end_time': chunk_end_time_ns,
                        'limit': 50
                    },
                    headers={"accept": "application/json"}
                )

                if response.status_code == 200:
                    data = response.json().get('funding_history', [])
                    if not data:
                        all_rates.append([None, None, None, None])
                        break
                    
                    all_rates.extend(data)
                    start_time = chunk_end_time

                    if len(data) < 50:
                        break  # Break if less than 50 records were returned
                else:
                    logging.error(f"Error fetching data for interval {interval_name}, status code: {response.status_code}")
                    break

            if all_rates:
                rates = [float(record[2]) for record in all_rates if record[2] is not None]

                if rates:
                    cumulative_rate = sum(rates)
                    median_record = all_rates[-1]
                    results.append({
                        'rate': str(cumulative_rate),
                        'price': median_record[3],
                        'time': interval_name
                    })
                else:
                    results.append({
                        'rate': None,
                        'price': None,
                        'time': interval_name
                    })
            else:
                results.append({
                    'rate': None,
                    'price': None,
                    'time': interval_name
                })

        return results
