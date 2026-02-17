# from pymongo import MongoClient

# client = MongoClient("mongodb://127.0.0.1:27017/")
# db = client["neurodiverse"]

# users = db["users"]





from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["neurodiverse"]
users = db["users"]

