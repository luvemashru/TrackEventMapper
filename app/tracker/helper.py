import json
from sanic import response
from bson import ObjectId
from marshmallow import ValidationError
from pymongo.errors import DuplicateKeyError
from app.tracker.serializer.request import (
    CreateTrackPlanRequestSchema, 
    GetTrackPlanRequestSchema, 
    UpdateTrackPlanRequestSchema
)
from app.tracker.serializer.response import GetTrackPlanResponseSchema
from app.event.helper import EventHelper
from database import TrackerDB
from database.track_plan import TrackPlanSchema

class TrackerHelper:
    def __init__(self, tracking_id=None):
        self.tracking_id = tracking_id

    @classmethod
    async def validate_create_tracking_plan_payload(self, data):
        # Validate Payload
        try:
            serialised_data = CreateTrackPlanRequestSchema().load(data.get("tracking_plan"))
        except ValidationError as e:
            raise ValidationError(e.messages)
        
        # Check if duplicate data is present
        validate_name = TrackerDB["track_plan"].find_one({"display_name":serialised_data.get("display_name")})
        if validate_name:
            raise DuplicateKeyError("Tracking Plan already present")
        
        # Serialised Data
        return serialised_data
    
    @classmethod
    async def trigger_create_event(self, events, id):
        '''This method can be called by create_plan and update_plan function'''
        
        # Create Event and Map with track_plan
        try:
            event_helper: response.json = await EventHelper(id, None).create_event(events.get("events"))
        except Exception as e:
            print(e)
        return json.loads(event_helper.body)
    
    @classmethod
    async def create_plan(self, data):
        '''Create Tracking Plan'''
        try:
            # This can return ValidationError and DuplicateKeyError
            serialised_data = await self.validate_create_tracking_plan_payload(data)
            
            # Validate the data against the schema and then load
            insert_data = TrackPlanSchema().load(serialised_data)
            return_response = TrackerDB["track_plan"].insert_one(insert_data)
            return_response=return_response.inserted_id
        
        # Exceptions to Handle
        except ValidationError as err:
            raise ValidationError(err.messages)
        except DuplicateKeyError as e:
            return {}, response.json({"message":"Name already present"}, status=400)
        
        # Create an event based.
        events_associated = serialised_data.get("rules", {})
        try:
            event_flow = await self.trigger_create_event(events_associated, str(return_response))
        except Exception as e:
            print(e)
        # Update is_active if event created successfully
        return_response = {
            "message":{
                "plan":"Plan added successfully",
                "events":event_flow.get("message",{})
            }
        }
        return response.json(return_response)
        
        
    
    @classmethod
    async def fetch_plan(self, params):
        # Serialise Params
        try:
            serialised_params = GetTrackPlanRequestSchema().load(params)
        except Exception as e:
            return response.json({"message":"Invalid Query Params"},status=400)
        
        # Fetch Query
        query = {}
        if serialised_params.get("display_name"):
            query["display_name"] = serialised_params["display_name"]
        
        if serialised_params.get("is_active"):
            query["is_active"] = serialised_params["is_active"]
        
        # Fetch the data from DB
        return_response = TrackerDB["track_plan"].find(query)
        return_response = [resp for resp in return_response]
        return GetTrackPlanResponseSchema().dump(return_response, many=True)

    async def update_plan(self, data):
        '''Update tracking plan'''
        # Serialise the data
        try:
            serialised_data = UpdateTrackPlanRequestSchema().load(data.get("tracking_plan"))
        except ValidationError as e:
            raise ValidationError(e.messages)
        
        # Check if plan is present in DB
        query = {"_id":ObjectId(self.tracking_id)}
        plan_present = TrackerDB["track_plan"].find(query)
        plan_present = [plan for plan in plan_present]
        if not plan_present:
            return response.json({"message": "No plan present"}, status=400)
        
        # Update the plan
        try:
            insert_data = TrackPlanSchema(partial=True).load(serialised_data)
            TrackerDB["track_plan"].update_one(query, {"$set":insert_data})
        except ValidationError as e:
            raise ValidationError(e.messages)
        
        return_response = {
            "message":{
                "plan":"Plan updated successfully",
                "events":{}
            }
        }
        if serialised_data.get("rules"):
            resp = await self.trigger_create_event(serialised_data.get("rules",{}), self.tracking_id)
            return_response["message"]["events"] = resp.get("message",{})
            
        return response.json(return_response)
        