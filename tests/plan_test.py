import pytest
from sanic import Sanic, response
from pymongo.errors import DuplicateKeyError
from marshmallow import ValidationError
from url import app_routes
from database import TrackerDB
from bson import ObjectId
from app.tracker.helper import TrackerHelper
from app.event.helper import EventHelper

@pytest.mark.asyncio
async def test_validate_create_tracking_plan_payload():
    data = {
        "tracking_plan": {
            "display_name": "Test Plan",
            "rules": {
                "events":[
                    {
                        "name":"track_event_1",
                        "description":"track_event_1",
                        "rules":{}
                    }
                ]
            }
        }
    }
    try:
        result = await TrackerHelper.validate_create_tracking_plan_payload(data)
        assert result == {
            "display_name": "Test Plan",
            "rules": {
                "events":[
                        {
                            "name":"track_event_1",
                            "description":"track_event_1",
                            "rules":{}
                        }
                    ]
            },
            "is_active":False
        }
    except Exception as e:
        assert isinstance(e, ValidationError) or isinstance(e, DuplicateKeyError)


@pytest.mark.asyncio
async def test_trigger_create_event():
    events = {"events":[{
        "name":"Test event track 1",
        "description":"Test",
        "rules":{}
    }]}
    id = "64d80f61e21be2addd9fd2b0"
    resp = await TrackerHelper.trigger_create_event(events, id)
    assert resp is not None


@pytest.mark.asyncio
async def test_create_plan():
    data = {
        "tracking_plan": {
            "display_name": "Test Plan create",
            "rules": {
                "events":[
                    {
                        "name":"track_event_1_create",
                        "description":"track_event_1",
                        "rules":{}
                    }
                ]
            }
        }
    }
    resp = await TrackerHelper.create_plan(data)
    assert resp.status == 200


@pytest.mark.asyncio
async def test_fetch_plan():
    params = {
        "display_name": "Test Plan create",
    }

    response = await TrackerHelper().fetch_plan(params)
    assert response is not None


@pytest.mark.asyncio
async def test_update_plan():
    TrackerDB["track_plan"].update_one({"_id":ObjectId("64d80f71e21be2addd9fd2b0")},{"$set":{
        "display_name":"Test Update Plan 12",
        "is_active":False,
        "_id":ObjectId("64d80f71e21be2addd9fd2b0")
    }}, upsert=True)
    data = {
        "tracking_plan":{
            "display_name": "Updated Tracking name"
        }
    }
    resp = await TrackerHelper("64d80f71e21be2addd9fd2b0").update_plan(data)
    assert resp.status == 200



@pytest.fixture
def app():
    app = Sanic("test_app")
    app.config.TESTING = True
    app.blueprint(app_routes)
    return app


@pytest.fixture
async def test_cli(loop, app, test_client):
    return loop.run_until_complete(test_client(app))