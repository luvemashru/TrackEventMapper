from pymongo import MongoClient, ASCENDING

def initialize_database():
    # Initialize MongoDB client
    client = MongoClient('mongodb://localhost:27017/')
    
    # Create or access the "Tracker" database
    db = client['Tracker']
    
    # Create collections if they don't exist
    track_plan_collection = db['track_plan']
    events_collection = db['events']
    event_plan_mapper_collection = db['event_plan_mapper']

    # Create Indexes for each
    track_plan_collection.create_index([('display_name', ASCENDING)], unique=True)
    events_collection.create_index([('name', ASCENDING)], unique=True)
    event_plan_mapper_collection.create_index([('event_id', ASCENDING), ('plan_id', ASCENDING)], unique=True)

    return db

TrackerDB = initialize_database()