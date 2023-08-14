from marshmallow import Schema, fields, EXCLUDE

class EventPlanMapperSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    event_id = fields.Str(required = True)
    tracker_id = fields.Str(require = True)