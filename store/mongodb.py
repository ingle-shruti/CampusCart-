import os
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["campuscart_db"]

products_collection = db["products"]
users_collection = db["users"]
orders_collection = db["orders"]

def save_product(product_data):
    result = products_collection.insert_one(product_data)
    return result.inserted_id


def save_order(order_data):
    result = orders_collection.insert_one(order_data)
    return result.inserted_id