import ccxt
import logging
from datetime import datetime, timezone
import numpy as np

from app.utils import get_timeframe, load_tickers, get_logo_url
from app.services.fr_service import FrService

class Gateio:
    @staticmethod
    def fetch_funding_rate_history(page, limit, time, sort_order, keyword):
        res = {
            "meta": {
                "v_platform": 'gateio-ccxt',
                "v_endpoint": "https://docs.ccxt.com/#/exchanges/gate?id=fetchfundinghistory",
                "v_docs": "https://docs.ccxt.com/#/exchanges/gate?id=fetchfundinghistory",
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
            funding_history = Gateio.fetchFundingWithCCXT('gateio', ticker_name, time)
            # data_per_ticker = {
            #     "coin": ticker_name.split('/')[0],
            #     "badge": ticker_name,
            #     "logo": get_logo_url(ticker_name.split('/')[0]),
            #     "rate": funding_history
            # }
            
            res['data'].append(str(funding_history))

        return res

        return funding_rates

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

            logging.debug(f"Funding history for {symbol}: {funding_history_dict}")

            # funding_time = [datetime.fromtimestamp(d["timestamp"] * 0.001) for d in funding_history_dict]
            funding_rate = [d["fundingRate"] * 100 for d in funding_history_dict]
            accumulation = np.sum(funding_rate)
            return accumulation

        except Exception as e:
            logging.error(f"Error fetching funding rate history: {e}")
            return None