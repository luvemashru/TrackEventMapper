from marshmallow import Schema, fields

class GetTrackPlanResponseSchema(Schema):
    display_name = fields.Str(required=True)
    is_active = fields.Bool(load_default=False)
    _id = fields.Str()