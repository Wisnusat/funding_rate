import requests
from datetime import datetime, timedelta

import logging
# Configure logging
logging.basicConfig(level=logging.DEBUG)

class aevo():
    @staticmethod
    def fetch_all_funding_history(page, limit, time, sort_order):
        ticker_aevo = ['10000SATS-PERP', '1000BONK-PERP', '1000PEPE-PERP', 'AEVO-PERP', 'ALT-PERP', 'APT-PERP', 'AR-PERP', 'ARB-PERP', 'ATOM-PERP', 'AVAX-PERP', 'AXL-PERP', 'BEAMX-PERP', 'BITCOIN-PERP', 'BLAST-PERP', 'BLUR-PERP', 'BLZ-PERP', 'BNB-PERP', 'BTC-PERP', 'CANTO-PERP', 'CRV-PERP', 'DOGE-PERP', 'DYDX-PERP', 'DYM-PERP', 'ENA-PERP', 'ETH-PERP', 'ETHFI-PERP', 'FTM-PERP', 'GLMR-PERP', 'HIFI-PERP', 'HPOS-PERP', 'ILV-PERP', 'INJ-PERP', 'JITO-PERP', 'JUP-PERP', 'LDO-PERP', 'LINK-PERP', 'MANTA-PERP', 'MATIC-PERP', 'MEME-PERP', 'MERL-PERP', 'MINA-PERP', 'MKR-PERP', 'MYRO-PERP', 'NEAR-PERP', 'NMR-PERP', 'NTRN-PERP', 'OMNI-PERP', 'OP-PERP', 'ORDI-PERP', 'OX-PERP', 'PARCL-PERP', 'PENDLE-PERP', 'PIXEL-PERP', 'PORTAL-PERP', 'PRIME-PERP', 'PYTH-PERP', 'SAGA-PERP', 'SEI-PERP', 'SHFL-PERP', 'SLERF-PERP', 'SOL-PERP', 'STRK-PERP', 'SUI-PERP', 'SYN-PERP', 'T-PERP', 'TAO-PERP', 'TIA-PERP', 'TNSR-PERP', 'TON-PERP', 'TRB-PERP', 'TRX-PERP', 'UMA-PERP', 'W-PERP', 'WIF-PERP', 'WLD-PERP', 'XRP-PERP', 'ZERO-PERP', 'ZETA-PERP']

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
            funding_history = aevo.fetch_single_funding_history(ticker_name, time)
            data_per_ticker = {
                "coin": ticker_name.split('-')[0],
                "badge": ticker_name,
                "logo": aevo.get_logo_url(ticker_name.split('-')[0]),
                "rates": funding_history
            }
            
            res['data'].append(data_per_ticker)

        return res

    @staticmethod
    def get_logo_url(ticker_symbol):
        name_mappings = {
            '10000SATS': 'bitcoin',
            '1000BONK': 'bonk',
            '1000PEPE': 'pepecoin',
            'AEVO': 'aevo',
            'ALT': 'altcoin',
            'APT': 'aptos',
            'AR': 'arweave',
            'ARB': 'arbitrum',
            'ATOM': 'cosmos',
            'AVAX': 'avalanche',
            'AXL': 'axelar',
            'BEAMX': 'beam',
            'BITCOIN': 'bitcoin',
            'BLAST': 'blast',
            'BLUR': 'blur',
            'BLZ': 'bluzelle',
            'BNB': 'binance-coin',
            'BTC': 'bitcoin',
            'CANTO': 'canto',
            'CRV': 'curve',
            'DOGE': 'dogecoin',
            'DYDX': 'dydx',
            'DYM': 'dym',
            'ENA': 'ena',
            'ETH': 'ethereum',
            'ETHFI': 'ethfi',
            'FTM': 'fantom',
            'GLMR': 'glimmer',
            'HIFI': 'hifi',
            'HPOS': 'hpos',
            'ILV': 'illuvium',
            'INJ': 'injective',
            'JITO': 'jito',
            'JUP': 'jupiter',
            'LDO': 'lido',
            'LINK': 'chainlink',
            'MANTA': 'mantle',
            'MATIC': 'polygon',
            'MEME': 'meme',
            'MERL': 'merlin',
            'MINA': 'mina',
            'MKR': 'maker',
            'MYRO': 'myro',
            'NEAR': 'near',
            'NMR': 'numeraire',
            'NTRN': 'ntrn',
            'OMNI': 'omni',
            'OP': 'optimism',
            'ORDI': 'ordi',
            'OX': 'ox',
            'PARCL': 'parcl',
            'PENDLE': 'pendle',
            'PIXEL': 'pixel',
            'PORTAL': 'portal',
            'PRIME': 'prime',
            'PYTH': 'pyth',
            'SAGA': 'saga',
            'SEI': 'sei',
            'SHFL': 'shfl',
            'SLERF': 'slerf',
            'SOL': 'solana',
            'STRK': 'strike',
            'SUI': 'sui',
            'SYN': 'syn',
            'T': 'threshold',
            'TAO': 'tao',
            'TIA': 'tia',
            'TNSR': 'tnsr',
            'TON': 'toncoin',
            'TRB': 'tellor',
            'TRX': 'tron',
            'UMA': 'uma',
            'W': 'w',
            'WIF': 'wif',
            'WLD': 'wld',
            'XRP': 'ripple',
            'ZERO': 'zero',
            'ZETA': 'zeta',
            # Add more mappings as needed
        }
        name = name_mappings.get(ticker_symbol.upper())
        if name:
            return f"https://cryptologos.cc/logos/{name}-{ticker_symbol.lower()}-logo.png"
        else:
            return None

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
        current_time = datetime.now()

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

            logging.debug(f"Fetching data for {ticker} interval {interval_name}, start time: {start_time}, end time: {end_time}")

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

                        # insert null data for the chunk
                        all_rates.append([None, None, None, None])
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
                # Filter out None values from the third element of the records
                rates = [float(record[2]) for record in all_rates if record[2] is not None]

                if rates:
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
                    logging.debug(f"No valid rates found for interval {interval_name}")
                    results.append({
                        'rate': None,
                        'price': None,
                        'time': interval_name,
                        'date': None
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

