from sqlalchemy import create_engine, func, cast, Numeric
from sqlalchemy.orm import sessionmaker
from app.utils import get_timeframe
from app.db.models import Base, AevoDB, BybitDB, GateioDB, HyperliquidDB
from app.config import Config

# Database connection setup
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

# Create tables in the database if they do not exist
Base.metadata.create_all(engine)

# Create a session factory
Session = sessionmaker(bind=engine)

def save_to_database(data, model_class):
    session = Session()  # Create a new session
    try:
        for entry in data:
            funding_record = model_class(
                instrument_name=entry[0],     
                timestamp=int(entry[1]),      
                funding_rate=entry[2],        
                mark_price=entry[3]           
            )
            session.add(funding_record)
        session.commit()
        print("Data saved successfully")
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
    finally:
        session.close()

def delete_all_data(model_class):
    session = Session()
    try:
        session.query(model_class).delete()
        session.commit()
        print("All data deleted successfully")
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
    finally:
        session.close()

def count_rows(model_class):
    session = Session()
    count = session.query(model_class).count()
    session.close()
    return count

# get instrument names from all exchanges and return a list of unique instrument names
def get_unique_tickers_from_all_exchanges():
    session = Session()
    aevo_tickers = session.query(AevoDB.instrument_name).distinct().all()
    bybit_tickers = session.query(BybitDB.instrument_name).distinct().all()
    gateio_tickers = session.query(GateioDB.instrument_name).distinct().all()
    hyperliquid_tickers = session.query(HyperliquidDB.instrument_name).distinct().all()
    all_tickers = aevo_tickers + bybit_tickers + gateio_tickers + hyperliquid_tickers
    unique_tickers = list(set([ticker[0] for ticker in all_tickers]))
    unique_tickers.sort()
    session.close()
    return unique_tickers

def get_accumulated_funding(model_class, since, until, keyword=None):
    session = Session()
    
    # Directly use since and until without multiplying by 1000
    if model_class == AevoDB:
        since = since * 1000000  # Convert seconds to microseconds
        until = until * 1000000
    elif model_class == GateioDB:
        since = since / 1000  # Convert milliseconds to seconds
        until = until / 1000
    elif model_class == HyperliquidDB:
        # Assume timestamps in HyperliquidDB are in milliseconds
        pass  # Do not modify since and until

    query = session.query(
        model_class.instrument_name,
        func.sum(cast(model_class.funding_rate, Numeric)).label('total_funding_rate')
    )

    # Apply timestamp filtering without flooring
    query = query.filter(
        model_class.timestamp >= since,
        model_class.timestamp <= until
    )

    # Apply the keyword filter if provided
    if keyword:
        query = query.filter(
            model_class.instrument_name == keyword.upper()
        )

    # Group by instrument name
    query = query.group_by(
        model_class.instrument_name
    )
    
    # Execute the query and fetch results
    data = query.all()
    session.close()
    return data

def get_accumulated_funding_pagination(model_class, page, limit, since, until, sort_order, keyword=None):
    session = Session()
    
    # Adjust timeframe handling based on the model class
    if model_class == AevoDB:
        since = since * 1000000  # Convert seconds to microseconds
        until = until * 1000000
    elif model_class == GateioDB:
        since = since / 1000  # Convert milliseconds to seconds
        until = until / 1000
    elif model_class == HyperliquidDB:
        # Assume timestamps in HyperliquidDB are in milliseconds
        pass  # Do not modify since and until

    # Build the base query with necessary filters
    query = session.query(
        model_class.instrument_name,
        func.sum(cast(model_class.funding_rate, Numeric)).label('total_funding_rate')
    ).filter(
        model_class.timestamp >= since,
        model_class.timestamp <= until
    )
    
    # Apply the keyword filter if a keyword is provided
    if keyword:
        query = query.filter(
            # model_class.instrument_name.ilike(f"%{keyword.upper()}%")
            model_class.instrument_name == keyword.upper()
        )
    
    # Group by instrument name
    query = query.group_by(
        model_class.instrument_name
    )
    
    # Apply sorting based on the sort_order parameter
    if sort_order == 'asc':
        query = query.order_by(model_class.instrument_name)
    elif sort_order == 'desc':
        query = query.order_by(model_class.instrument_name.desc())
    else:
        raise ValueError("Invalid sort order. Use 'asc' or 'desc'.")
    
    # Apply pagination
    query = query.offset((page - 1) * limit).limit(limit)
    
    # Execute the query and fetch results
    data = query.all()
    session.close()
    
    return data
