import requests
import logging
from datetime import datetime, timezone
from app.utils import load_tickers, get_logo_url, get_timeframe

import ccxt
import numpy as np

# Configure logging
logging.basicConfig(level=logging.DEBUG)

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

        # if keyword is provided, filter the list of tickers
        if keyword:
            tickers = [ticker for ticker in tickers if keyword.lower() in ticker.lower()]

        # Sort the ticker list
        if sort_order == 'desc':
            tickers.sort(reverse=True)
        else:
            tickers.sort()

        # Pagination
        total_items = len(tickers)
        res["meta"]["totalItems"] = total_items
        res["meta"]["totalPages"] = (total_items // limit) + (1 if total_items % limit != 0 else 0)
        res["meta"]["isNextPage"] = page * limit < total_items

        # Apply pagination to tickers
        start = (page - 1) * limit
        end = start + limit
        tickers_paginated = tickers[start:end]

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
    def fetchFundingWithCCXT(exchange: str, symbol: str, timeframe: str) -> tuple:
        try:
            ex = getattr(ccxt, exchange)()
            params = {}
            since = None
            if timeframe is not None:
                since, until = get_timeframe(timeframe)
                params['until'] = until
            funding_history_dict = ex.fetch_funding_rate_history(symbol, since=since, params=params)
            # funding_time = [datetime.fromtimestamp(d["timestamp"] * 0.001) for d in funding_history_dict]
            funding_rate = [d["fundingRate"] * 100 for d in funding_history_dict]
            accumulation = np.sum(funding_rate)
            return accumulation

        except Exception as e:
            logging.error(f"Error fetching funding rate history: {e}")
            return None