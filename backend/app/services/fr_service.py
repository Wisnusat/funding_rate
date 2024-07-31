import requests
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class FrService:
    @staticmethod
    def get_market_pairs_from_aevo():
        try:
            url = "https://api.aevo.xyz/assets"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Market Pairs from Aevo: {data}")
            # Correctly extract the pairs from the data
            return [asset['symbol'] for asset in data['assets']]
        except Exception as e:
            logging.error(f"Error getting market pairs from Aevo: {str(e)}")
            return []

    @staticmethod
    def get_fr_aevo():
        try:
            url = "https://api.aevo.xyz/funding-history?limit=50"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Funding Rates from Aevo: {data}")
            # Correctly parse the data using 'funding_history' key
            funding_rates = []
            for entry in data['funding_history']:
                try:
                    funding_rates.append({
                        'symbol': entry[0],
                        'timestamp': entry[1],
                        'rate': float(entry[2])
                    })
                except ValueError as ve:
                    logging.error(f"Error converting rate to float: {entry[2]} - {str(ve)}")
            return funding_rates
        except Exception as e:
            logging.error(f"Error getting funding rates from Aevo: {str(e)}")
            return []

    @staticmethod
    def get_all_rates(duration, page, limit, keywords):
        res = {
            "meta": {
                "page": page,
                "perPage": limit,
                "totalPages": 0,
                "totalItems": 0,
                "isNextPage": False,
            },
            "data": []
        }

        # Get pairs from Aevo
        pairs = FrService.get_market_pairs_from_aevo()
        logging.debug(f"Pairs: {pairs}")
        
        # Get funding rates from Aevo
        aevo_fr = FrService.get_fr_aevo()
        logging.debug(f"Aevo Funding Rates: {aevo_fr}")

        # Process and match funding history with pairs
        processed_data = []
        for symbol in pairs:
            asset_name = symbol.split('-')[0]
            aevo_rates = []
            for entry in aevo_fr:
                logging.debug(f"Checking entry: {entry}")  # Debugging statement
                if entry['symbol'] == symbol:
                    logging.debug(f"Matching entry: {entry}")  # Debugging statement
                    aevo_rates.append(entry['rate'])

            logging.debug(f"Rates for {symbol}: {aevo_rates}")  # Debugging statement

            average_rate = lambda rates: sum(rates) / len(rates) if rates else None
            format_rate = lambda rate: f"{rate:.2%}" if rate is not None else "N/A"

            average = average_rate(aevo_rates)

            processed_data.append({
                "coin": asset_name,
                "badge": symbol,
                "logo": f"https://cryptologos.cc/logos/{asset_name.lower()}-{symbol.lower()}-logo.png",
                "average": format_rate(average),
                "hyperliquid": "N/A",
                "aevo": format_rate(average_rate(aevo_rates)),
                "bybit": "N/A",
                "gateio": "N/A"
            })
        logging.debug(f"Processed Data: {processed_data}")
        
        # Apply filtering based on keywords
        if keywords:
            processed_data = [entry for entry in processed_data if keywords.lower() in entry['coin'].lower()]

        # Paginate results
        total_items = len(processed_data)
        total_pages = (total_items + limit - 1) // limit
        is_next_page = page < total_pages

        start = (page - 1) * limit
        end = start + limit
        paginated_data = processed_data[start:end]

        # Update meta information
        res['meta']['totalItems'] = total_items
        res['meta']['totalPages'] = total_pages
        res['meta']['isNextPage'] = is_next_page
        res['data'] = paginated_data

        return res
