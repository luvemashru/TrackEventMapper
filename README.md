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

2. 2 Microservice type folders are created:
    1. event (Handles all the event related changes Create | Update | GET)
    2. tracker (Handles all the tracker related changes Create | Update | GET)

3. Folder structure:
    1. `app` Folder contains APIs
    2. `database` Folder contains DB Schema and indexes for all collections
    3. `tests` folder contains all the test cases