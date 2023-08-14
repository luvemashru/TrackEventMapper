# Data Tracker & Event Inspector
---
Backend uses following Techstacks:
1. Python3.9
2. Sanic
3. Mongo DB
---

To install dependencies, run:
```shell
setup_script.sh
```
To start the server, run:
```shell
run.sh
```

---
## General Update about the implementation:
1. Database `Tracker` is used which has 3 collections:
    1. `track_plan`
        - Contains details about the Tracking Plan, which is attached to the source.
    2. `events`
        - Contains details about the Events that are present in Tracking Plan.
        - Kept this as a separate collection, since it's a separate entity and can be associated with multiple plans.
    3. `event_plan_mapper`
        - This is the mapper, which maps Tracking Plan with the event present.
        - Hence, the index for this database is: [tracker_id, event_id], since that will be the unique one.

2. APIs are integrated in such a way that:
    1. POST /tracking-plan:
        - Creates a new plan.
        - Validation of track_plan payload
        - After creating a plan, 
            - it will trigger create event function call internally.
        - Mantaining a boolean variable: `is_active` in `track_plan` collection, which will be set to true when the event is create and mapped to the tracker.
    2. GET /tracking-plan
    3 . POST /events
        - We are keeping a tracking_id field compulsory over here, since each event 
        should be associated to atleast one tracking_plan.