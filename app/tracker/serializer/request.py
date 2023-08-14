from marshmallow import Schema, fields, ValidationError, post_load, EXCLUDE

class EventSchema(Schema):
    events = fields.List(fields.Dict, required = True)
    
    @post_load
    def check_events(self, data, **kwargs):
        if not data.get("events"):
            raise ValidationError("Events should to be present while creating tracking plan")
        return data


class CreateTrackPlanRequestSchema(Schema):
    display_name = fields.Str(required=True)
    rules = fields.Nested(EventSchema, required=True)
    is_active = fields.Bool(load_default=False)

class UpdateTrackPlanRequestSchema(Schema):
    class Meta:
        unknown=EXCLUDE
    display_name = fields.Str()
    rules = fields.Nested(EventSchema)

class GetTrackPlanRequestSchema(Schema):
    display_name = fields.Str()
    is_active = fields.Bool()