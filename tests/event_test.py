import pytest
from sanic import Sanic, response
from app.event.helper import EventHelper
from pymongo.errors import DuplicateKeyError
from marshmallow import ValidationError
from url import app_routes
from database import TrackerDB
from bson import ObjectId

async def test_validate_create_event_payload():
    helper_obj = EventHelper()
    
    # Create test data
    data = [
        {
            "name": "event1",
            "description": "description1",
            "rules":{}
        },
        {
            "name": "event2",
            "description": "description2",
            "rules":{}
        }
    ]
    
    # Validate payload
    try:
        result = await helper_obj.validate_create_event_payload(data)
        assert result == data
    except Exception as e:
        assert isinstance(e, DuplicateKeyError)


async def test_map_plan_event():
    helper_obj = EventHelper(tracking_id="64d89f61e21be2addd9fd2b0", event_id="64d8a00fe21be2addd9fd2b9")
    
    # Create test data
    data = [
        "64d8a00fe21be2addd9fd2b9",
        "64d8a00fe21be2addd9fd2ba"
    ]

    payload = {
        "_id":ObjectId("64d89f61e21be2addd9fd2b0"),
        "display_name":"Test 1",
        "is_active":False
    }
    query = {"_id":ObjectId("64d89f61e21be2addd9fd2b0")}
    TrackerDB["track_plan"].update_one(query, {"$set":payload}, upsert=True)
    
    # Map events to plan
    try:
        result = await helper_obj.map_plan_event(data)
        assert result is None
    except Exception as e:
        assert isinstance(e, ValidationError) or isinstance(e, DuplicateKeyError)


async def test_create_event():
    helper_obj = EventHelper()
    
    # Create test data
    data = [
        {
            "name": "event1",
            "description": "description1",
            "rules":{}
        },
        {
            "name": "event2",
            "description": "description2",
            "rules":{}
        }
    ]
    
    # Create events
    try:
        result = await helper_obj.create_event(data)
        assert result.status == 200
    except Exception as e:
        assert isinstance(e, ValidationError) or isinstance(e, DuplicateKeyError)


async def test_update_event():
    event = TrackerDB["events"].find_one({"name": "event2"})
    helper_obj = EventHelper(event_id=str(event.get("_id")))
    
    # Create test data
    data = {
        "name": "updated_event1",
        "description": "updated_description1"
    }
    
    # Update event
    try:
        result = await helper_obj.update_event(data)
        assert result.status == 200
    except Exception as e:
        assert isinstance(e, ValidationError) or isinstance(e, DuplicateKeyError)


async def test_fetch_events():
    helper_obj = EventHelper()
    
    # Create test data
    params = {
        "name": "event1"
    }
    
    # Fetch events
    try:
        result = await helper_obj.fetch_events(params)
        assert result is not None
    except Exception as e:
        assert isinstance(e, ValidationError)


async def test_verify_plan_event():
    TrackerDB["track_plan"].update_one({"_id":ObjectId("64d80f61e21be2addd9fd2b0")},{"$set":{
        "display_name":"Test Plan 2",
        "is_active":False,
        "_id":ObjectId("64d80f61e21be2addd9fd2b0")
    }}, upsert=True)

    TrackerDB["events"].update_one({"_id":ObjectId("64d8a00fe20be2addd9fd2b9"),},{"$set":{
        "_id":ObjectId("64d8a00fe20be2addd9fd2b9"),
        "name": "test_event3",
        "description": "updated_description1",
        "rules":{}
    }}, upsert=True)
    helper_obj = EventHelper(event_id="64d8a00fe20be2addd9fd2b9", tracking_id="64d80f61e21be2addd9fd2b0")
    
    # Verify plan event
    try:
        result = await helper_obj.verify_plan_event()
        assert result.status == 200
    except Exception as e:
        assert isinstance(e, ValidationError) or isinstance(e, DuplicateKeyError)


@pytest.fixture
def app():
    app = Sanic("test_app")
    app.config.TESTING = True
    app.blueprint(app_routes)
    return app


@pytest.fixture
async def test_cli(loop, app, test_client):
    return loop.run_until_complete(test_client(app))
