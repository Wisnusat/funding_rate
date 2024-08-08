import ccxt
import logging
from datetime import datetime, timezone
import numpy as np

from app.utils import get_timeframe, load_tickers, get_logo_url
from app.services.fr_service import FrService

class Bybit:
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
            ticker_name = f"{ticker_name}/USDT:USDT"
            funding_history = FrService.fetchFundingWithCCXT('bybit', ticker_name, time)
            # data_per_ticker = {
            #     "coin": ticker_name.split('/')[0],
            #     "badge": ticker_name,
            #     "logo": get_logo_url(ticker_name.split('/')[0]),
            #     "rate": funding_history
            # }
            
            res['data'].append(str(funding_history))

        return res

        return funding_rates

