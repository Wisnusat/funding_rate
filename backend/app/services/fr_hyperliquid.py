import ccxt
import logging
from datetime import datetime, timezone
import numpy as np

from app.utils import get_timeframe, load_tickers, get_logo_url

class Hyperliquid:
    @staticmethod
    def fetch_and_accumulate_funding(exchange: str, symbol: str, timeframe: str) -> tuple:
        """
        Fetch funding rates on perpetual contracts listed on the exchange.

        Args:
            exchange (str): Name of exchange (binance, bybit, ...)
            symbol (str): Symbol (BTC/USDT:USDT, ETH/USDT:USDT, ...).
            timeframe (str): Timeframe (1h, 1d, 7d, 1M, 1y).
            limit (int): The maximum amount of funding rate structures to fetch.

        Returns (tuple): settlement time, funding rate.
        """
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

    @staticmethod
    def fetch_funding_rate_history(page, limit, time, sort_order, keyword):
        res = {
            "meta": {
                "v_platform": 'hyperliquid-ccxt',
                "v_endpoint": "https://docs.ccxt.com/#/exchanges/hyperliquid?id=fetchfundingratehistory",
                "v_docs": "https://docs.ccxt.com/#/exchanges/hyperliquid?id=fetchfundingratehistory",
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
            ticker_name = f"{ticker_name}/USDC:USDC"
            funding_history = Hyperliquid.fetch_and_accumulate_funding('hyperliquid', ticker_name, time)
            # data_per_ticker = {
            #     "coin": ticker_name.split('/')[0],
            #     "badge": ticker_name,
            #     "logo": get_logo_url(ticker_name.split('/')[0]),
            #     "rate": funding_history
            # }
            
            res['data'].append(str(funding_history))

        return res

        return funding_rates

