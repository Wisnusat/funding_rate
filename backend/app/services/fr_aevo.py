import requests
from datetime import datetime, timedelta, timezone
from app.utils import load_tickers, get_logo_url
import logging
# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Aevo():
    @staticmethod
    def fetch_all_funding_history(page, limit, time, sort_order, keyword):
        ticker_aevo = load_tickers()

        # if keyword is provided, filter the list of tickers
        if keyword:
            ticker_aevo = [ticker for ticker in ticker_aevo if keyword.lower() in ticker.lower()]

        res = {
            "meta": {
                "v_platform": "aevo",
                "v_endpoint": "https://api.aevo.xyz/funding-history",
                "v_docs": "https://api-docs.aevo.xyz/reference/getfundinghistory",
                "page": page,
                "perPage": limit,
                "totalPages": 0,
                "totalItems": 0,
                "isNextPage": False,
                "date": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z'),
            },
            "data": []
        }

        # Sort the ticker_aevo list
        if sort_order == 'desc':
            ticker_aevo.sort(reverse=True)
        else:
            ticker_aevo.sort()

        # Pagination
        total_items = len(ticker_aevo)
        res["meta"]["totalItems"] = total_items
        res["meta"]["totalPages"] = (total_items // limit) + (1 if total_items % limit != 0 else 0)
        res["meta"]["isNextPage"] = page * limit < total_items

        # Apply pagination to ticker_aevo
        start = (page - 1) * limit
        end = start + limit
        ticker_aevo_paginated = ticker_aevo[start:end]

        for ticker_name in ticker_aevo_paginated:
            ticker_name = f"{ticker_name}-PERP"
            funding_history = Aevo.fetch_single_funding_history(ticker_name, time)
            # data_per_ticker = {
                # "coin": ticker_name.split('-')[0],
                # "badge": ticker_name,
                # "logo": get_logo_url(ticker_name.split('-')[0]),
                # "rate": funding_history[0]['rate'] if funding_history else None,
                # "price": funding_history[0]['price'] if funding_history else None,
                # "time": funding_history[0]['time'] if funding_history else None
            # }
            
            res['data'].append(funding_history[0]['rate'] if funding_history else None)

        return res

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

        # get interval by time parameter
        if time in intervals:
            intervals = {time: intervals[time]}


        for interval_name, interval_delta in intervals.items():
            end_time = current_time  # Each interval's end_time is now
            start_time = end_time - interval_delta
            if interval_name == '1h':
                chunk = 1
            else:
                chunk = 10
            chunk_size = interval_delta / chunk  # Adjust the chunk size if needed

            # logging.debug(f"Fetching data for {ticker} interval {interval_name}, start time: {start_time}, end time: {end_time}")

            all_rates = []
            total_data_points = 0  # Counter for the total data points
            while start_time < end_time:
                chunk_end_time = min(start_time + chunk_size, end_time)
                start_time_ns = int(start_time.timestamp() * 1_000_000_000)
                chunk_end_time_ns = int(end_time.timestamp() * 1_000_000_000)
                
                if time == '1h':
                    start_time_ns = int(0)
                    # chunk_end_time_ns = int(0)
                

                response = requests.get(
                    'https://api.aevo.xyz/funding-history',
                    params={
                        'instrument_name': ticker,
                        'start_time': start_time_ns,
                        'end_time': chunk_end_time_ns,
                        'limit': 50  # max 50
                    },
                    headers={"accept": "application/json"}
                )

                if response.status_code == 200:
                    data = response.json().get('funding_history', [])
                    if not data:
                        # logging.debug(f"No data fetched for interval {interval_name}, chunk start time: {start_time}, chunk end time: {chunk_end_time}")
                        # insert null data for the chunk
                        all_rates.append([None, None, None, None])
                        break
                    
                    all_rates.extend(data)
                    total_data_points += len(data)  # Update the counter
                    start_time = chunk_end_time

                    if len(data) < 50:
                        break  # Break if less than 50 records were returned
                else:
                    logging.error(f"Error fetching data for interval {interval_name}, status code: {response.status_code}")
                    break

            if all_rates:
                # Filter out None values from the third element of the records
                rates = [float(record[2]) for record in all_rates if record[2] is not None]

                if rates:
                    # Calculate cumulative sum
                    cumulative_rate = sum(rates)
                    median_record = all_rates[-1]
                    results.append({
                        'rate': str(cumulative_rate),
                        'price': median_record[3],
                        'time': interval_name
                    })
                else:
                    # logging.debug(f"No valid rates found for interval {interval_name}")
                    results.append({
                        'rate': None,
                        'price': None,
                        'time': interval_name
                    })
            else:
                # logging.debug(f"No data found for interval {interval_name}")
                results.append({
                    'rate': None,
                    'price': None,
                    'time': interval_name
                })

        return results

