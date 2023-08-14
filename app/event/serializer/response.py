from marshmallow import fields, Schema

class GetEventResponseSchema(Schema):
    name = fields.Str()
    description = fields.Str()
    rules = fields.Dict()
    _id = fields.Str()