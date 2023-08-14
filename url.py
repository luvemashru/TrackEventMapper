from sanic import Blueprint
from app.tracker.views import TrackPlan
from app.event.views import Event

app_routes = Blueprint.group(TrackPlan, Event)