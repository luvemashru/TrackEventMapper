from marshmallow import Schema, fields

class EventsSchema(Schema):
    name = fields.Str(required = True)
    description = fields.Str(required=True)
    rules = fields.Dict(required=True)