import ccxt
import logging
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor

from app.utils import get_timeframe, load_tickers, get_logo_url
from app.services.fr_service import FrService

logging.basicConfig(level=logging.WARNING)  # Adjust logging level to reduce verbosity

class Bybit:
    @staticmethod
    def fetch_funding_data(ticker_name, time):
        ticker_name = f"{ticker_name}/USDT:USDT"
        funding_history = FrService.fetchFundingWithCCXT('bybit', ticker_name, time)
        return str(funding_history)

    @staticmethod
    def paginate_list(items, page, limit):
        start = (page - 1) * limit
        end = start + limit
        return items[start:end]

    @staticmethod
    def fetch_funding_rate_history(page, limit, time, sort_order, keyword):
        res = {
            "meta": {
                "v_platform": 'bybit-ccxt',
                "v_endpoint": "https://docs.ccxt.com/#/exchanges/bybit?id=fetchfundingratehistory",
                "v_docs": "https://docs.ccxt.com/#/exchanges/bybit?id=fetchfundingratehistory",
                "page": page,
                "perPage": limit,
                "totalPages": 0,
                "totalItems": 0,
                "isNextPage": False,
                "date": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z'),
            },
            "data": []
        }

        tickers = load_tickers()
        if keyword:
            tickers = [ticker for ticker in tickers if keyword.lower() in ticker.lower()]
        if sort_order == 'desc':
            tickers.sort(reverse=True)
        else:
            tickers.sort()

        total_items = len(tickers)
        res["meta"]["totalItems"] = total_items
        res["meta"]["totalPages"] = (total_items // limit) + (1 if total_items % limit != 0 else 0)
        res["meta"]["isNextPage"] = page * limit < total_items

        tickers_paginated = Bybit.paginate_list(tickers, page, limit)

        with ThreadPoolExecutor() as executor:
            results = list(executor.map(lambda ticker: Bybit.fetch_funding_data(ticker, time), tickers_paginated))

        res['data'] = results
        return res
