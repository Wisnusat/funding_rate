from app.db.models import AevoDB, BybitDB, GateioDB, HyperliquidDB
from app.db.operations import get_accumulated_funding, get_accumulated_funding_pagination, get_unique_tickers_from_all_exchanges
from collections import defaultdict
from decimal import Decimal
import datetime
from app.utils import get_logo_url

def get_tickers():
    tickers = get_unique_tickers_from_all_exchanges()
    return tickers

def get_funding_aevo(time, keyword):
    # data = get_accumulated_funding_pagination(AevoDB, page, limit, time, sort_order, keyword)
    data = get_accumulated_funding(AevoDB, time, keyword)
    return data

def get_funding_bybit(time, keyword):
    data = get_accumulated_funding(BybitDB, time, keyword)
    return data

def get_funding_gateio(time, keyword):
    data = get_accumulated_funding(GateioDB, time, keyword)
    return data

def get_funding_hyperliquid(time, keyword):
    data = get_accumulated_funding(HyperliquidDB, time, keyword)
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
def scrapper(interval='1d', coin=None):
    unique_tickers = get_tickers()
    aevo = get_funding_aevo(interval, coin)
    bybit = get_funding_bybit(interval, coin)
    gateio = get_funding_gateio(interval, coin)
    hyperliquid = get_funding_hyperliquid(interval, coin)
    
    aggregated_data = aggregate_funding_data(unique_tickers, aevo, bybit, gateio, hyperliquid)
    return aggregated_data

# Pagination
def get_funding_aevo_pagination(page, limit, time, sort_order, keyword):
    data = get_accumulated_funding_pagination(AevoDB, page, limit, time, sort_order, keyword)
    return data

def get_funding_bybit_pagination(page, limit, time, sort_order, keyword):
    data = get_accumulated_funding_pagination(BybitDB, page, limit, time, sort_order, keyword)
    return data

def get_funding_gateio_pagination(page, limit, time, sort_order, keyword):
    data = get_accumulated_funding_pagination(GateioDB, page, limit, time, sort_order, keyword)
    return data

def get_funding_hyperliquid_pagination(page, limit, time, sort_order, keyword):
    data = get_accumulated_funding_pagination(HyperliquidDB, page, limit, time, sort_order, keyword)
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

# Main function to get paginated and aggregated funding data
# def scrapper_with_pagination(page=1, limit=10, interval='1d', sort_order='asc', coin=None):
#     unique_tickers = get_unique_tickers_from_all_exchanges()
#     aevo = get_funding_aevo_pagination(1, 100, interval, sort_order, coin)  # Fetch more than needed for aggregation
#     bybit = get_funding_bybit_pagination(1, 100, interval, sort_order, coin)
#     gateio = get_funding_gateio_pagination(1, 100, interval, sort_order, coin)
#     hyperliquid = get_funding_hyperliquid_pagination(1, 100, interval, sort_order, coin)
    
#     aggregated_data = aggregate_funding_data_pagination(unique_tickers, aevo, bybit, gateio, hyperliquid)

#     # Apply pagination to the aggregated data
#     start_index = (page - 1) * limit
#     end_index = start_index + limit
#     paginated_data = dict(list(aggregated_data.items())[start_index:end_index])
    
#     return paginated_data

def scrapper_with_pagination(page=1, limit=10, interval='1d', sort_order='asc', coin=None):
    unique_tickers = get_unique_tickers_from_all_exchanges()
    aevo = get_funding_aevo_pagination(1, 100, interval, sort_order, coin)  # Fetch more than needed for aggregation
    bybit = get_funding_bybit_pagination(1, 100, interval, sort_order, coin)
    gateio = get_funding_gateio_pagination(1, 100, interval, sort_order, coin)
    hyperliquid = get_funding_hyperliquid_pagination(1, 100, interval, sort_order, coin)
    
    aggregated_data = aggregate_funding_data_pagination(unique_tickers, aevo, bybit, gateio, hyperliquid)

    # Apply pagination to the aggregated data
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
                "aevo": funding_data["aevo"],
                "bybit": funding_data["bybit"],
                "gateio": funding_data["gateio"],
                "hyperliquid": funding_data["hyperliquid"]
            }
        })

    # Construct the meta information
    total_pages = (total_items + limit - 1) // limit  # Ceiling division
    is_next_page = page < total_pages

    meta = {
        "date": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "isNextPage": is_next_page,
        "page": page,
        "perPage": limit,
        "totalItems": total_items,
        "totalPages": total_pages
    }

    return {"data": data, "meta": meta}