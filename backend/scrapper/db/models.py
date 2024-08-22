import uuid
import json
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, BigInteger, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from utils.common import nanoseconds_to_datetime

Base = declarative_base()

class AevoDB(Base):
    __tablename__ = 'funding_data_aevo'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    instrument_name = Column(String, nullable=False)
    timestamp = Column(BigInteger, nullable=False)
    funding_rate = Column(String, nullable=False)
    mark_price = Column(String)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<AevoDB(instrument_name={self.instrument_name}, timestamp={self.timestamp}, funding_rate={self.funding_rate}, mark_price={self.mark_price})>"

    def to_dict(self):
        # Only include fields that are safe to expose in the API
        return {
            # 'id': str(self.id),  # Convert UUID to string
            'instrument_name': self.instrument_name,
            'timestamp': self.timestamp,
            'funding_rate': self.funding_rate,
            # 'mark_price': self.mark_price,
            # 'created_at': self.created_at.isoformat() if self.created_at else None,
            # 'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

class BybitDB(Base):
    __tablename__ = 'funding_data_bybit'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    instrument_name = Column(String, nullable=False)
    timestamp = Column(BigInteger, nullable=False)
    funding_rate = Column(String, nullable=False)
    mark_price = Column(String)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<BybitDB(instrument_name={self.instrument_name}, timestamp={self.timestamp}, funding_rate={self.funding_rate}, mark_price={self.mark_price})>"

    def to_dict(self):
        # Only include fields that are safe to expose in the API
        return {
            # 'id': str(self.id),  # Convert UUID to string
            'instrument_name': self.instrument_name,
            'timestamp': self.timestamp,
            'funding_rate': self.funding_rate,
            # 'mark_price': self.mark_price,
            # 'created_at': self.created_at.isoformat() if self.created_at else None,
            # 'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

class GateioDB(Base):
    __tablename__ = 'funding_data_gateio'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    instrument_name = Column(String, nullable=False)
    timestamp = Column(BigInteger, nullable=False)
    funding_rate = Column(String, nullable=False)
    mark_price = Column(String)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<GateioDB(instrument_name={self.instrument_name}, timestamp={self.timestamp}, funding_rate={self.funding_rate}, mark_price={self.mark_price})>"

    def to_dict(self):
        # Only include fields that are safe to expose in the API
        return {
            # 'id': str(self.id),  # Convert UUID to string
            'instrument_name': self.instrument_name,
            'timestamp': self.timestamp,
            'funding_rate': self.funding_rate,
            # 'mark_price': self.mark_price,
            # 'created_at': self.created_at.isoformat() if self.created_at else None,
            # 'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)

class HyperliquidDB(Base):
    __tablename__ = 'funding_data_hyperliquid'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    instrument_name = Column(String, nullable=False)
    timestamp = Column(BigInteger, nullable=False)
    funding_rate = Column(String, nullable=False)
    mark_price = Column(String)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<HyperliquidDB(instrument_name={self.instrument_name}, timestamp={self.timestamp}, funding_rate={self.funding_rate}, mark_price={self.mark_price})>"

    def to_dict(self):
        # Only include fields that are safe to expose in the API
        return {
            # 'id': str(self.id),  # Convert UUID to string
            'instrument_name': self.instrument_name,
            'timestamp': self.timestamp,
            'funding_rate': self.funding_rate,
            # 'mark_price': self.mark_price,
            # 'created_at': self.created_at.isoformat() if self.created_at else None,
            # 'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)