from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from db.models import AevoDB, BybitDB, GateioDB, HyperliquidDB

class AevoDBSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = AevoDB
        load_instance = True

class BybitDBSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = BybitDB
        load_instance = True

class GateioDBSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = GateioDB
        load_instance = True

class HyperliquidDBSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = HyperliquidDB
        load_instance = True