from sanic import response
from bson import ObjectId
from marshmallow import ValidationError
from pymongo.errors import DuplicateKeyError
from app.event.serializer.request import (
    CreateEventRequestSchema, 
    GetEventRequestSchema, 
    UpdateEventRequestSchema
)
from app.event.serializer.response import GetEventResponseSchema
from database import TrackerDB
from database.events import EventsSchema
from database.event_plan_mapper import EventPlanMapperSchema

class EventHelper:
    def __init__(self, tracking_id = None, event_id=None):
        self.tracking_id = tracking_id
        self.event_id = event_id

    async def validate_create_event_payload(self, data):
        '''Validate payload and check for other event with same name'''
        
        # This will raise validation error, if schema is not present
        serialised_data = CreateEventRequestSchema().load(data, many=True)
        
        # Check if duplicate data is present
        names = [event.get("name") for event in serialised_data]
        validate_name = TrackerDB["events"].find({"name":{"$in":names}})
        validate_name = [name for name in validate_name]
        if validate_name:
            
            # Separate the new events that can be added
            events_present = {name.get("name"):name for name in validate_name}
            events_to_add = [event 
                                for event in serialised_data
                                if not events_present.get(event.get("name"))
                            ]
            
            # If there are events that can be added, add it
            if events_to_add:
                events_to_add = EventsSchema().load(events_to_add, many=True)
                resp = TrackerDB["events"].insert_many(events_to_add)                
                # Add the event to event_plan_mapper
                if self.tracking_id:
                    await self.map_plan_event(resp.inserted_ids)
            
            # Raise a duplicate key error
            events_to_add = [event.get("name") for event in events_to_add]
            duplicateKeyErrorMessage = {
                "events_not_added":list(events_present.keys()),
                "events_added": events_to_add
            }
            raise DuplicateKeyError(duplicateKeyErrorMessage)
        
        # Return serialised_data if there is no Exception raised
        return serialised_data

    async def map_plan_event(self, data):
        '''Map event along with it's tracking id'''
        # Generate payload to be added
        data_to_map =  [
            {
                "event_id": str(event),
                "tracker_id": self.tracking_id
            }
            for event in data
        ]
        
        # Return if nothing is present
        if not data_to_map:
            return
        
        try:
            # Insert the mapped data
            serialised_data = EventPlanMapperSchema().load(data_to_map, many=True)
            TrackerDB["event_plan_mapper"].insert_many(serialised_data)
            
            # Update the plan is_active status to True
            query = {"_id":ObjectId(self.tracking_id)}
            TrackerDB["track_plan"].update_one(query, {"$set":{"is_active":True}})
        
        # Exception Handling
        except ValidationError as e:
            raise ValidationError(e.messages)
        except DuplicateKeyError as e:
            raise DuplicateKeyError(e._message)
        


    async def create_event(self, events):
        try:
            serialised_data = await self.validate_create_event_payload(events)
            serialised_data = EventsSchema().load(events, many=True)
            return_response = TrackerDB["events"].insert_many(serialised_data).inserted_ids
        except ValidationError as err:
            return response.json({"message":err.messages, "error":"validation"}, status=400)
        except DuplicateKeyError as e:
            return response.json({"message":e._message, "error":"key_error"})

        # Add the event to event_plan_mapper
        if self.tracking_id:
            await self.map_plan_event(return_response)

        names = [data.get("name") for data in serialised_data]
        return_response = {"message":{"events_not_added":[], "events_added":names}, "error":""}
        return response.json(return_response, status = 200)


    async def update_event(self, event):
        try:
            serialised_data = UpdateEventRequestSchema().load(event)
            serialised_data = EventsSchema().load(serialised_data, partial=True)
        except ValidationError as e:
            return response.json({"message":e.messages}, status=400)
        
        if not self.event_id:
            return response.json({"message":"event_id is not present"}, status=400)
        
        query = {"_id":ObjectId(self.event_id)}
        event_present = TrackerDB["events"].find(query)
        if not event_present:
            return response.json({"message":f"event with {self.event_id} is not present"}, status=400)
        
        try:
            TrackerDB["events"].update_one(query, {"$set":serialised_data})
        except DuplicateKeyError as e:
            return response.json({"message":"Similar Event name already exists"}, status=400)
        return_response = {"message":"Event Updated Successfully"}
        return response.json(return_response, status = 200)



    @classmethod
    async def fetch_events(self, params):
        # Serialise Params
        try:
            serialised_params = GetEventRequestSchema().load(params)
        except Exception as e:
            return response.json({"message":"Invalid Query Params"},status=400)
        
        # Fetch Query
        query = {}
        if serialised_params.get("name"):
            query["name"] = serialised_params["name"]
        
        # Fetch the data from DB
        return_response = TrackerDB["events"].find(query)
        return [GetEventResponseSchema().dump(resp) for resp in return_response]

    async def verify_plan_event(self):
        if self.event_id:
            # Verify is event exists
            event = TrackerDB["events"].find_one({"_id":ObjectId(self.event_id)})
            if not event:
                return response.json({"message":"Event not present"}, status=400)

        if self.tracking_id:    
            # Verify if plan exists
            plan = TrackerDB["track_plan"].find_one({"_id":ObjectId(self.tracking_id)})
            if not plan:
                return response.json({"message":"Plan not present"}, status=400)
            
        try:
            await self.map_plan_event([self.event_id])
        except Exception as e:
            return response.json({"message":"Mapping already present"}, status=400)
        
        return response.json({"message":"Mapping added successfully"})
        '''http://localhost:8000/tracking-plan/64d89f61e21be2addd9fd2b0/event/64d8a00fe21be2addd9fd2b9'''