import uuid
import json
from sqlalchemy import create_engine, func, cast, Numeric, desc, asc
from sqlalchemy.orm import sessionmaker
from app.utils import get_timeframe
from app.logger import logger
from app.db.models import Base, AevoDB, BybitDB, GateioDB, HyperliquidDB
from app.config import Config

# Database connection setup
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

# Create tables in the database if they do not exist
Base.metadata.create_all(engine)

# Create a session factory
Session = sessionmaker(bind=engine)

def save_to_database(data, model_class):
    with Session() as session:
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
            return True
        except Exception as e:
            session.rollback()
            return e

def delete_all_data(model_class):
    with Session() as session:
        try:
            session.query(model_class).delete()
            session.commit()
            logger.info("All data deleted successfully")
        except Exception as e:
            session.rollback()
            logger.error(f"An error occurred: {e}")

def delete_old_data(model_class):
    with Session() as session:
        try:
            # Menghitung batas waktu 1 tahun yang lalu dari waktu sekarang
            one_year_ago = int((datetime.now() - timedelta(days=366)).timestamp())

            # Menghapus data yang memiliki timestamp lebih dari 1 tahun
            session.query(model_class).filter(model_class.timestamp < one_year_ago).delete()
            session.commit()
            logger.info("Old data deleted successfully")
        except Exception as e:
            session.rollback()
            logger.error(f"An error occurred while deleting old data: {e}")

def count_rows(model_class):
    with Session() as session:
        return session.query(model_class).count()

def get_unique_tickers_from_all_exchanges():
    with Session() as session:
        tickers = (
            session.query(AevoDB.instrument_name)
            .union(session.query(BybitDB.instrument_name))
            .union(session.query(GateioDB.instrument_name))
            .union(session.query(HyperliquidDB.instrument_name))
            .distinct()
            .all()
        )
        return sorted([ticker[0] for ticker in tickers])

def get_tickers(keyword=None):
    with Session() as session:
        tickers = (
            session.query(AevoDB.instrument_name)
            .union(session.query(BybitDB.instrument_name))
            .union(session.query(GateioDB.instrument_name))
            .union(session.query(HyperliquidDB.instrument_name))
            .distinct()
            .all()
        )
        
        # Filter tickers based on the keyword if provided
        filtered_tickers = [
            ticker[0] for ticker in tickers 
            if keyword is None or keyword.lower() in ticker[0].lower()
        ]
        
        return sorted(filtered_tickers)

def adjust_timeframe(model_class, since, until):
    if model_class == AevoDB:
        since, until = since * 1000000, until * 1000000  # Convert seconds to microseconds
    # HyperliquidDB assumed to use milliseconds, no changes needed
    return since, until

def build_base_query(session, model_class, since, until, keyword):
    since, until = adjust_timeframe(model_class, since, until)
    query = session.query(
        model_class.instrument_name,
        # Multiply the sum of the funding rate by 100 to get the percentage
        (func.sum(cast(model_class.funding_rate, Numeric)) * 100).label('total_funding_rate_percentage')
    ).filter(
        model_class.timestamp >= since,
        # model_class.timestamp <= until
    )
    if keyword:
        query = query.filter(model_class.instrument_name == keyword.upper())
    return query.group_by(model_class.instrument_name)


def get_latest_funding_data(session, model_class, keyword=None):
    # Subquery to get the latest timestamp for each unique instrument
    latest_funding_subquery = session.query(
        model_class.instrument_name,
        func.max(model_class.timestamp).label('latest_timestamp')
    ).group_by(
        model_class.instrument_name
    ).subquery()

    # Main query to get the full data for the latest funding rates
    query = session.query(
        model_class.instrument_name,
        model_class.funding_rate,
    ).join(
        latest_funding_subquery,
        (model_class.instrument_name == latest_funding_subquery.c.instrument_name) &
        (model_class.timestamp == latest_funding_subquery.c.latest_timestamp)
    )

    # Apply the keyword filter if provided (case insensitive)
    if keyword:
        query = query.filter(model_class.instrument_name.ilike(f"%{keyword}%"))

    # Order by instrument_name in ascending order (or modify to 'desc' for descending)
    query = query.order_by(model_class.instrument_name.asc())

    # Return the result
    return query.all()

def get_accumulated_funding_pagination(model_class, page, limit, since, until, sort_order, keyword=None):
    with Session() as session:
        # Query with time range filter
        query = build_base_query(session, model_class, since, until, keyword)
        
        # Apply sorting based on the provided order
        order = asc if sort_order == 'asc' else desc
        query = query.order_by(order(model_class.instrument_name))
        
        # Apply pagination
        result = query.offset((page - 1) * limit).limit(limit).all()
        
        # If no results are found, get the latest data without pagination
        if not result:
            # Fetch the latest data using the previously fixed function
            result = get_latest_funding_data(session, model_class, keyword)  # No need to wrap in a list
        
        return result

def get_accumulated_funding(model_class, since, until, keyword=None):
    with Session() as session:
        # Query with time range filter
        query = build_base_query(session, model_class, since, until, keyword)
        result = query.all()
        
        # If no results are found with the time range, get the latest data
        if not result:
            result = get_latest_funding_data(session, model_class, keyword)
        
        # Make sure the result is handled correctly (depending on how many columns are expected)
        if isinstance(result, list):
            # Unpacking result if it's a list of tuples
            return [(instrument_name, funding_rate, timestamp) for instrument_name, funding_rate, timestamp in result]
        else:
            return result
