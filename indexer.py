from pymongo import MongoClient

client = MongoClient

client = MongoClient('127.0.0.1', 27017)

db = client.isitsteaknight

menus = db.menus

print(menus.find_one())
