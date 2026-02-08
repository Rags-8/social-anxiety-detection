from pymongo import MongoClient
from bson import ObjectId, errors
import os

MONGO_DETAILS = os.getenv("MONGODB_URI", "mongodb://localhost:27017")

client = MongoClient(MONGO_DETAILS)

# FIXED: Use correct database and collection names
database = client["mindcare_db"]

# Collections
chats_collection = database["chats"]

# Helpers

def chat_helper(chat) -> dict:
    return {
        "id": str(chat["_id"]),
        "user_id": chat.get("user_id"),
        "message": chat.get("message"),
        "response": chat.get("response"),
        "anxiety_level": chat.get("anxiety_level"),
        "timestamp": chat.get("timestamp")
    }

def delete_chat(id: str):
    try:
        # FIXED: Ensure valid ObjectId conversion
        if not ObjectId.is_valid(id):
            print(f"DEBUG: Invalid ObjectId format: {id}")
            return False
            
        oid = ObjectId(id)
        result = chats_collection.delete_one({"_id": oid})
        
        if result.deleted_count > 0:
            print(f"DEBUG: Successfully deleted document with id: {id}")
            return True
        else:
            print(f"DEBUG: No document found with id: {id}")
            return False
            
    except errors.InvalidId:
        print(f"DEBUG: InvalidId exception for: {id}")
        return False
    except Exception as e:
        print(f"Database Delete Error: {e}")
        return False
