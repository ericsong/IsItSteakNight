from pymongo import MongoClient

client = MongoClient

client = MongoClient('127.0.0.1', 27017)

db = client.isitsteaknight

menus = db.menus

for menu in menus.find():
    for item in menu['data']:
        location_name = item['location_name']
        for meal in item['meals']:
            if(meal['meal_avail']):
                for genre in meal['genres']:
                    genre_name = genre['genre_name']
                    for item in genre['items']:
                        print(location_name + ': ' + genre_name + ': ' + item)
