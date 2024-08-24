from app.db.models import AevoDB, BybitDB, GateioDB, HyperliquidDB
from app.db.operations import get_tickers, get_accumulated_funding_pagination, get_unique_tickers_from_all_exchanges
from collections import defaultdict
from datetime import datetime
from app.utils import get_logo_url, get_timeframe

def get_coins(keyword=None):
    # Assuming get_unique_tickers is a function that retrieves the unique tickers based on the keyword
    unique_tickers = get_tickers(keyword)
    
    # Construct the data array with the required fields
    data = []
    for ticker in unique_tickers:
        logo_url, name = get_logo_url(ticker)
        data.append({
            "coin": ticker,
            "logo": logo_url or "https://www.imghippo.com/i/ZBzQI1724488120.webp",
            "name": name or ticker
        })

    return data

# Generic function to get paginated funding data for any exchange
def get_funding_pagination(db_model, page, limit, since, until, sort_order, keyword):
    return get_accumulated_funding_pagination(db_model, page, limit, since, until, sort_order, keyword)

# Aggregate funding data for multiple exchanges
def aggregate_funding_data(unique_tickers, data_sources):
    aggregated_data = defaultdict(lambda: {key: None for key in data_sources.keys()})

    for source_name, data in data_sources.items():
        for ticker, funding in data:
            if ticker in unique_tickers:
                aggregated_data[ticker][source_name] = str(funding) if funding is not None else None

    return dict(aggregated_data)

# Main function to get aggregated funding data with pagination
def scrapper_with_pagination(page=1, limit=10, time='1d', sort_order='asc', coin=None):
    since, until = get_timeframe(time)
    unique_tickers = get_unique_tickers_from_all_exchanges()

    if coin:
        unique_tickers = [ticker for ticker in unique_tickers if ticker.lower() == coin.lower()]

    # Fetch paginated data from each exchange
    data_sources = {
        'aevo': get_funding_pagination(AevoDB, 1, 100, since, until, sort_order, coin),
        'bybit': get_funding_pagination(BybitDB, 1, 100, since, until, sort_order, coin),
        'gateio': get_funding_pagination(GateioDB, 1, 100, since, until, sort_order, coin),
        'hyperliquid': get_funding_pagination(HyperliquidDB, 1, 100, since, until, sort_order, coin)
    }

    aggregated_data = aggregate_funding_data(unique_tickers, data_sources)

    # Ensure that tickers with no data are still included
    if not aggregated_data:
        aggregated_data = {ticker: {source: None for source in data_sources} for ticker in unique_tickers}

    # Apply pagination
    total_items = len(aggregated_data)
    start_index = (page - 1) * limit
    end_index = start_index + limit
    paginated_items = list(aggregated_data.items())[start_index:end_index]

    # Construct the data array with the required fields
    data = [{
        "coin": ticker,
        "logo": logo_url or "https://www.imghippo.com/i/ZBzQI1724488120.webp",
        "name": name or ticker,
        "funding": funding_data
    } for ticker, funding_data in paginated_items for logo_url, name in [get_logo_url(ticker)]]

    # Meta information
    total_pages = (total_items + limit - 1) // limit
    is_next_page = page < total_pages

    meta = {
        "filter": {"time": time, "coin": coin or "All", "sortOrder": sort_order},
        "date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "isNextPage": is_next_page,
        "page": page,
        "perPage": limit,
        "totalItems": total_items,
        "totalPages": total_pages
    }

    return {"data": data, "meta": meta}
