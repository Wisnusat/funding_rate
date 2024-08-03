import requests
import logging
from datetime import datetime, timezone
from app.utils import load_tickers, get_logo_url

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
            data_per_ticker = {
                "coin": ticker_name.split('-')[0],
                "badge": ticker_name,
                "logo": get_logo_url(ticker_name.split('-')[0]),
            }
            
            res['data'].append(data_per_ticker)

        return res
