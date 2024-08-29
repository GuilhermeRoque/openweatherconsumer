import datetime
import os

from pymongo import MongoClient

mongo_url = os.getenv('MONGO_URL', 'mongodb://127.0.0.1:27017/')
client = MongoClient(mongo_url)
db = client['async_requests']
collection = db['openweather_requests']

def insert_task(
    user_id: str,
    task_id: str = None
):
    document = {
        "user_id": user_id,
        "task_id": task_id,
        "timestamp": datetime.datetime.utcnow(),
        "progress": 0,
        "status": "PROGRESS",
        "results": []
    }
    collection.insert_one(document=document)
    return {"message": "Document added successfully"}

def update_task(
        user_id: str,
        progress: int,
        new_result: dict,
        status: str
):
    filter_query = {"user_id": user_id}
    update_data = {
        "$set": {
            "progress": progress,
            "status": status
        },
        "$push": {
            "results": new_result
        },
    }
    collection.update_one(filter=filter_query, update=update_data)
    return {"message": "Document updated successfully"}

def abort_task(
        user_id: str
):
    filter_query = {"user_id": user_id}
    update_data = {
        "$set": {
            "status": "FAILED"
        },
    }
    collection.update_one(filter=filter_query, update=update_data)
    return {"message": "Document updated successfully"}

def read_task(user_id: str):
    return collection.find_one({"user_id": user_id})
