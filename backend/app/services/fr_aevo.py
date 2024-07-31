import requests
from datetime import datetime, timedelta

import logging
# Configure logging
logging.basicConfig(level=logging.DEBUG)

class aevo():
    @staticmethod
    def fetch_all_funding_history(page, limit, keywords):
        ticker_aevo = ['BTC-PERP', 'ETH-PERP', 'SOL-PERP']
        res = {
            "meta": {
                "platform": "aevo",
                "endpoint": "https://api.aevo.xyz/funding-history",
                "page": page,
                "perPage": limit,
                "totalPages": 0,
                "totalItems": 0,
                "isNextPage": False,
            },
            "data": []
        }
        
        for ticker_name in ticker_aevo:
            funding_history = aevo.fetch_single_funding_history(ticker_name)
            data_per_ticker = {
                "coin": ticker_name.split('-')[0],
                "badge": ticker_name,
                "logo": aevo.get_logo_url(ticker_name.split('-')[0]),
                "rates": funding_history
            }
            
            res['data'].append(data_per_ticker)
        
        # Pagination
        total_items = len(res['data'])
        res["meta"]["totalItems"] = total_items
        res["meta"]["totalPages"] = (total_items // limit) + (1 if total_items % limit != 0 else 0)
        res["meta"]["isNextPage"] = page * limit < total_items
        
        # Apply pagination
        start = (page - 1) * limit
        end = start + limit
        res['data'] = res['data'][start:end]

        return res

    @staticmethod
    def get_logo_url(ticker_symbol):
        name_mappings = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'SOL': 'solana',
            # Add more mappings as needed
        }
        name = name_mappings.get(ticker_symbol.upper())
        if name:
            return f"https://cryptologos.cc/logos/{name}-{ticker_symbol.lower()}-logo.png"
        else:
            return None

    @staticmethod
    def fetch_single_funding_history(ticker):
        intervals = {
            '1h': timedelta(hours=1),
            '1d': timedelta(days=1),
            '7d': timedelta(days=7),
            '1M': timedelta(days=30),
            '1y': timedelta(days=365)
        }
        results = []
        current_time = datetime.now()

        for interval_name, interval_delta in intervals.items():
            end_time = current_time  # Each interval's end_time is now
            start_time = end_time - interval_delta
            if interval_name == '1h':
                chunk = 1
            else:
                chunk = 10
            chunk_size = interval_delta / chunk  # Adjust the chunk size if needed

            logging.debug(f"Fetching data for interval {interval_name}, start time: {start_time}, end time: {end_time}")

            all_rates = []
            total_data_points = 0  # Counter for the total data points
            while start_time < end_time:
                chunk_end_time = min(start_time + chunk_size, end_time)
                start_time_ns = int(start_time.timestamp() * 1_000_000_000)
                chunk_end_time_ns = int(chunk_end_time.timestamp() * 1_000_000_000)

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
                        logging.debug(f"No data fetched for interval {interval_name}, chunk start time: {start_time}, chunk end time: {chunk_end_time}")
                        break
                    
                    all_rates.extend(data)
                    total_data_points += len(data)  # Update the counter

                    logging.debug(f"Interval {interval_name}: Fetched {len(data)} data points. Total so far: {total_data_points}")

                    start_time = chunk_end_time

                    if len(data) < 50:
                        break  # Break if less than 50 records were returned
                else:
                    logging.error(f"Error fetching data for interval {interval_name}, status code: {response.status_code}")
                    break

            if all_rates:
                rates = [float(record[2]) for record in all_rates]
                rates.sort()
                median_index = len(rates) // 2
                if len(rates) % 2 == 0:
                    median_rate = (rates[median_index - 1] + rates[median_index]) / 2
                else:
                    median_rate = rates[median_index]

                median_record = all_rates[median_index]

                results.append({
                    'rate': median_record[2],
                    'price': median_record[3],
                    'time': interval_name,
                    'date': datetime.fromtimestamp(int(median_record[1]) / 1_000_000_000).strftime('%Y-%m-%d %H:%M:%S')
                })
            else:
                logging.debug(f"No data found for interval {interval_name}")
                results.append({
                    'rate': None,
                    'price': None,
                    'time': interval_name,
                    'date': None
                })

        return results

