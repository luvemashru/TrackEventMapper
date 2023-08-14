import json
from marshmallow import Schema, fields, ValidationError, pre_load

def validate_rules(rules):
    try:
        json.dumps(rules)
    except (TypeError, OverflowError):
        raise ValidationError("rules field must be a valid json")

class CreateEventRequestSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str(required=True)
    rules = fields.Dict(required=True, validate=validate_rules)

class UpdateEventRequestSchema(Schema):
    name = fields.Str()
    description = fields.Str()
    rules = fields.Dict(validate=validate_rules)

class GetEventRequestSchema(Schema):
    name = fields.Str()