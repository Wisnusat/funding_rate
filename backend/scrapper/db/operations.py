from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.common import get_timeframe
from db.models import Base

# Database connection setup
# DATABASE_URL = "postgresql://admindev:admindev@localhost:5432/funding_data_scrape"
DATABASE_URL = "postgresql://postgres.uzgtuydizbithgjjcnko:hbLkWC5ytDDpGj87@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
engine = create_engine(DATABASE_URL)

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
    
def get_data_by_params(model_class, instrument_name='btc', interval='1d'):
    session = Session()
    try:
        start_time, end_time = get_timeframe(interval)
        if instrument_name:
            data = session.query(model_class).filter(
                model_class.instrument_name == instrument_name,
                model_class.timestamp >= start_time,
                model_class.timestamp <= end_time
            ).all()
        else:
            data = session.query(model_class).filter(
                model_class.timestamp >= start_time,
                model_class.timestamp <= end_time
            ).all()
        
        return data

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        session.close()