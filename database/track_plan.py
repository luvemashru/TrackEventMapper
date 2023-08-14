from marshmallow import Schema, fields, EXCLUDE

class TrackPlanSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    display_name = fields.Str(required = True)
    is_active = fields.Bool(required = True)