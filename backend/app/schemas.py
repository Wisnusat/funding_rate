from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.UUID(load_only=True)
    username = fields.Str(required=True)
    password = fields.Str(load_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
