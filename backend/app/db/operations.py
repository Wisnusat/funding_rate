import uuid
import json
from sqlalchemy import create_engine, func, cast, Numeric, desc, asc
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
            print("Data saved successfully")
        except Exception as e:
            session.rollback()
            print(f"An error occurred: {e}")

def delete_all_data(model_class):
    with Session() as session:
        try:
            session.query(model_class).delete()
            session.commit()
            print("All data deleted successfully")
        except Exception as e:
            session.rollback()
            print(f"An error occurred: {e}")

def delete_old_data(model_class):
    with Session() as session:
        try:
            # Menghitung batas waktu 1 tahun yang lalu dari waktu sekarang
            one_year_ago = int((datetime.now() - timedelta(days=366)).timestamp())

            # Menghapus data yang memiliki timestamp lebih dari 1 tahun
            session.query(model_class).filter(model_class.timestamp < one_year_ago).delete()
            session.commit()
            print("Old data deleted successfully")
        except Exception as e:
            session.rollback()
            print(f"An error occurred while deleting old data: {e}")

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
    elif model_class == GateioDB:
        since, until = since / 1000, until / 1000  # Convert milliseconds to seconds
    # HyperliquidDB assumed to use milliseconds, no changes needed
    return since, until

def build_base_query(session, model_class, since, until, keyword):
    since, until = adjust_timeframe(model_class, since, until)
    query = session.query(
        model_class.instrument_name,
        func.sum(cast(model_class.funding_rate, Numeric)).label('total_funding_rate')
    ).filter(
        model_class.timestamp >= since,
        # model_class.timestamp <= until
    )
    if keyword:
        query = query.filter(model_class.instrument_name == keyword.upper())
    return query.group_by(model_class.instrument_name)

def get_accumulated_funding(model_class, since, until, keyword=None):
    with Session() as session:
        query = build_base_query(session, model_class, since, until, keyword)
        return query.all()

def get_accumulated_funding_pagination(model_class, page, limit, since, until, sort_order, keyword=None):
    with Session() as session:
        query = build_base_query(session, model_class, since, until, keyword)
        
        # Apply sorting
        order = asc if sort_order == 'asc' else desc
        query = query.order_by(order(model_class.instrument_name))
        
        # Apply pagination
        return query.offset((page - 1) * limit).limit(limit).all()
