from sanic import Sanic
from pymongo import MongoClient
from url import app_routes
from database import TrackerDB

app = Sanic(__name__)

# Import routes from url.py
app.blueprint(app_routes)

if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True)
