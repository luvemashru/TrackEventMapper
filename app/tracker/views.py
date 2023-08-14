import json
from sanic import Blueprint
from sanic import response
from marshmallow import Schema, fields, ValidationError
from pymongo.errors import DuplicateKeyError

from app.tracker.serializer.request import CreateTrackPlanRequestSchema
from app.tracker.helper import TrackerHelper
from app.event.helper import EventHelper

TrackPlan = Blueprint('track_plan')

class TrackingPlan:
    '''
    Tracking Plan related to a source are created, updated and stored here.
    '''
    @TrackPlan.route('/tracking-plan', methods=['POST'])
    async def create_tracking_plan(request):
        '''
        Create a tracking plan
            - Create a tracking plan
            - Create an event associated to the tracking plan
        '''
        # Object Initialisation and Data extrction
        tracker_helper = TrackerHelper()  
        data = json.loads(request.body)      
        
        # Create the tracker
        return_response = await tracker_helper.create_plan(data)
        return return_response

    @TrackPlan.route('/tracking-plan', methods=['GET'])
    async def get_tracking_plans(request):
        '''
        Fetch Tracking Plan based on plan name and is_active
        '''
        result = await TrackerHelper.fetch_plan(request.args)
        return response.json(result)
    
    @TrackPlan.route("/tracking-plan/<id>", methods=['PATCH'])
    async def update_tracking_plan(request, id):
        # Extract Data from request
        data = json.loads(request.body)

        # Update the plan
        return_response = await TrackerHelper(id).update_plan(data)

        # return the response
        return (return_response)


    @TrackPlan.route("/tracking-plan/<id>/event/<event_id>", methods=["PUT"])
    async def map_plan_event(request, id, event_id):
        '''Map event with track plan'''
        return_response = await EventHelper(id, event_id).verify_plan_event()
        return return_response