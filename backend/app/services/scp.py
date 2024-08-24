from app.db.models import AevoDB, BybitDB, GateioDB, HyperliquidDB
from app.db.operations import get_accumulated_funding, get_accumulated_funding_pagination, get_unique_tickers_from_all_exchanges
from collections import defaultdict
from decimal import Decimal
import datetime
from app.utils import get_logo_url, get_timeframe

def get_tickers():
    tickers = get_unique_tickers_from_all_exchanges()
    return tickers

def get_funding_aevo(since, until, keyword):
    data = get_accumulated_funding(AevoDB, since, until, keyword)
    return data

def get_funding_bybit(since, until, keyword):
    data = get_accumulated_funding(BybitDB, since, until, keyword)
    return data

def get_funding_gateio(since, until, keyword):
    data = get_accumulated_funding(GateioDB, since, until, keyword)
    return data

def get_funding_hyperliquid(since, until, keyword):
    data = get_accumulated_funding(HyperliquidDB, since, until, keyword)
    return data

def aggregate_funding_data(unique_tickers, aevo_data, bybit_data, gateio_data, hyperliquid_data):
    # Create a dictionary to hold the aggregated data
    aggregated_data = defaultdict(lambda: {'aevo': None, 'bybit': None, 'gateio': None, 'hyperliquid': None})

    # Helper function to insert data into the aggregated_data dictionary
    def insert_data(source_name, data):
        for ticker, funding in data:
            if ticker in unique_tickers:
                # Directly assign the funding, convert to string if needed
                aggregated_data[ticker][source_name] = str(funding) if funding is not None else None

    # Insert data from each source
    insert_data('aevo', aevo_data)
    insert_data('bybit', bybit_data)
    insert_data('gateio', gateio_data)
    insert_data('hyperliquid', hyperliquid_data)

    return dict(aggregated_data)

# Main function to get aggregated funding data
def scrapper(time='1d', coin=None):
    since, until = get_timeframe(time)

    unique_tickers = get_tickers()
    aevo = get_funding_aevo(since, until, coin)
    bybit = get_funding_bybit(since, until, coin)
    gateio = get_funding_gateio(since, until, coin)
    hyperliquid = get_funding_hyperliquid(since, until, coin)
    
    aggregated_data = aggregate_funding_data(unique_tickers, aevo, bybit, gateio, hyperliquid)
    return aggregated_data

# ========================================================================================================
# Pagination
def get_funding_aevo_pagination(page, limit, since, until, sort_order, keyword):
    data = get_accumulated_funding_pagination(AevoDB, page, limit, since, until, sort_order, keyword)
    return data

def get_funding_bybit_pagination(page, limit, since, until, sort_order, keyword):
    data = get_accumulated_funding_pagination(BybitDB, page, limit, since, until, sort_order, keyword)
    return data

def get_funding_gateio_pagination(page, limit, since, until, sort_order, keyword):
    data = get_accumulated_funding_pagination(GateioDB, page, limit, since, until, sort_order, keyword)
    return data

def get_funding_hyperliquid_pagination(page, limit, since, until, sort_order, keyword):
    data = get_accumulated_funding_pagination(HyperliquidDB, page, limit, since, until, sort_order, keyword)
    return data

def aggregate_funding_data_pagination(unique_tickers, aevo_data, bybit_data, gateio_data, hyperliquid_data):
    # Create a dictionary to hold the aggregated data
    aggregated_data = defaultdict(lambda: {'aevo': None, 'bybit': None, 'gateio': None, 'hyperliquid': None})

    # Helper function to insert data into the aggregated_data dictionary
    def insert_data(source_name, data):
        for ticker, funding in data:
            if ticker in unique_tickers:
                # Directly assign the funding, convert to string if needed
                aggregated_data[ticker][source_name] = str(funding) if funding is not None else None

    # Insert data from each source
    insert_data('aevo', aevo_data)
    insert_data('bybit', bybit_data)
    insert_data('gateio', gateio_data)
    insert_data('hyperliquid', hyperliquid_data)

    return dict(aggregated_data)

# Main function to get aggregated funding data with pagination
def scrapper_with_pagination(page=1, limit=10, time='1d', sort_order='asc', coin=None):
    since, until = get_timeframe(time)

    unique_tickers = get_unique_tickers_from_all_exchanges()

    # If a specific coin is provided, filter the unique_tickers accordingly
    if coin:
        unique_tickers = [ticker for ticker in unique_tickers if ticker.lower() == coin.lower()]
    
    aevo = get_funding_aevo_pagination(1, 100, since, until, sort_order, coin)  # Fetch more than needed for aggregation
    bybit = get_funding_bybit_pagination(1, 100, since, until, sort_order, coin)
    gateio = get_funding_gateio_pagination(1, 100, since, until, sort_order, coin)
    # hyperliquid = get_funding_hyperliquid_pagination(1, 100, since, until, sort_order, coin)
    hyperliquid = []

    aggregated_data = aggregate_funding_data_pagination(unique_tickers, aevo, bybit, gateio, hyperliquid)

    # Apply pagination to the aggregated data
    total_items = len(aggregated_data)
    
    if total_items == 0:
        # If no data is available, add unique tickers with null data
        for ticker in unique_tickers:
            aggregated_data[ticker] = {
                "aevo": None,
                "bybit": None,
                "gateio": None,
                "hyperliquid": None
            }
        total_items = len(aggregated_data)
    
    start_index = (page - 1) * limit
    end_index = start_index + limit
    paginated_items = list(aggregated_data.items())[start_index:end_index]

    # Construct the data array with the required fields
    data = []
    for ticker, funding_data in paginated_items:
        logo_url, name = get_logo_url(ticker)
        data.append({
            "coin": ticker,
            "logo": logo_url or "https://cryptologos.cc/logos/default-logo.png",  # Fallback logo if not found
            "name": name or ticker,  # Fallback to ticker if name not found
            "funding": {
                "aevo": funding_data.get("aevo", None),
                "bybit": funding_data.get("bybit", None),
                "gateio": funding_data.get("gateio", None),
                "hyperliquid": funding_data.get("hyperliquid", None)
            }
        })

    # Construct the meta information
    total_pages = (total_items + limit - 1) // limit  # Ceiling division
    is_next_page = page < total_pages

    meta = {
        "filter": {
            "time": time,
            "coin": coin or "All",
            "sortOrder": sort_order
        },
        "date": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "isNextPage": is_next_page,
        "page": page,
        "perPage": limit,
        "totalItems": total_items,
        "totalPages": total_pages
    }

    return {"data": data, "meta": meta}


