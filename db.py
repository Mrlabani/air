from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users = db.users
downloads = db.downloads

def add_user(user_id):
    users.update_one({"_id": user_id}, {"$set": {"_id": user_id}}, upsert=True)

def log_download(user_id, file_name):
    downloads.insert_one({
        "user_id": user_id,
        "file": file_name
    })

def get_stats():
    return {
        "total_users": users.count_documents({}),
        "total_downloads": downloads.count_documents({})
    }
