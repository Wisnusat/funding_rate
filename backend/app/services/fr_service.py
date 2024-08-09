import requests
import logging
from datetime import datetime, timezone
import ccxt
import numpy as np
from functools import lru_cache

from app.utils import load_tickers, get_logo_url, get_timeframe

logging.basicConfig(level=logging.WARNING)  # Configure logging level

class FrService:
    @staticmethod
    def tickers(page, limit, time, sort_order, keyword):
        res = {
            "meta": {
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

        tickers_paginated = FrService.paginate_list(tickers, page, limit)

        for ticker_name in tickers_paginated:
            logo, name = get_logo_url(ticker_name.split('/')[0])
            data_per_ticker = {
                "coin": ticker_name.split('-')[0],
                "badge": ticker_name,
                "logo": logo,
                "name": name
            }
            
            res['data'].append(data_per_ticker)

        return res

    @staticmethod
    @lru_cache(maxsize=128)
    def fetchFundingWithCCXT(exchange: str, symbol: str, timeframe: str) -> tuple:
        try:
            ex = getattr(ccxt, exchange)()
            params = {}
            since = None
            if timeframe is not None:
                since, until = get_timeframe(timeframe)
                params['until'] = until
            funding_history_dict = ex.fetch_funding_rate_history(symbol, since=since, params=params)
            funding_rate = [d["fundingRate"] * 100 for d in funding_history_dict]
            accumulation = np.sum(funding_rate)
            # Return "None" if accumulation is 0.0, otherwise return the accumulation as a string
            return "None" if accumulation == 0.0 else str(accumulation)

        except Exception as e:
            logging.error(f"Error fetching funding rate history: {e}")
            return None

    @staticmethod
    def paginate_list(items, page, limit):
        start = (page - 1) * limit
        end = start + limit
        return items[start:end]
