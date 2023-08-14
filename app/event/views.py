import json
from sanic import Blueprint
from sanic import response
from pymongo import MongoClient
from marshmallow import Schema, fields
from app.event.helper import EventHelper

Event = Blueprint('event')

class EventCreate:
    @Event.route('/events', methods=['POST'])
    async def create_event(request):
        '''Create events'''
        
        # Object Initialisation and Data extraction
        event_helper = EventHelper() 
        data = json.loads(request.body)
        
        # Create Event Flow
        return_response = await event_helper.create_event(data.get("events"))
        
        # Analyse response and send
        return return_response

    @Event.route('/events', methods=['GET'])
    async def get_events(request):
        '''
        GET all the events based on name
        '''
        result = await EventHelper.fetch_events(request.args)
        return response.json(result)

    @Event.route("/events/<id>", methods=["PATCH"])
    async def update_tracking_plan(request, id):
        '''
        Update Tracking Plan
        '''
        data = json.loads(request.body)
        return_response = await EventHelper(None, id).update_event(data.get("events"))
        return return_response
    