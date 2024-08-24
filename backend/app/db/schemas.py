from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.db.models import User, AevoDB, BybitDB, GateioDB, HyperliquidDB

# User schema
class UserSchema(Schema):
    id = fields.UUID(load_only=True)
    username = fields.Str(required=True)
    password = fields.Str(load_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

# AevoDB schema
class AevoDBSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = AevoDB
        load_instance = True

# BybitDB schema
class BybitDBSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = BybitDB
        load_instance = True

# GateioDB schema
class GateioDBSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = GateioDB
        load_instance = True

# HyperliquidDB schema
class HyperliquidDBSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = HyperliquidDB
        load_instance = True
