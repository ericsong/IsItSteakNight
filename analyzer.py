import time
import string
import psycopg2
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client.isitsteaknight

menus = db.menus

try:
    conn = psycopg2.connect("host='localhost' dbname='isitsteaknight' user='iisn_admin' password='abc123'")
except:
    print("I am unable to connect to the database")

cur = conn.cursor()

cur.execute("""
SELECT "Genre".name as genre, "Item".name as item FROM "Genre" INNER JOIN "Item" ON "Item".genre = "Genre".id
""")

def validGenre(genre):
    genre_lower = genre.lower()
    if (
        genre_lower == "entrees" or
        genre_lower == "nightly promo" or
        genre_lower == "cook to order bar"
        ):
        return True

    return False

def miscFlags(item):
    item_lower = item.lower()
    if "philly" in item_lower:
        return False

    return True

def isSteakItem(genre, item):
    item_lower = item.lower()
    if "steak" in item_lower and validGenre(genre) and miscFlags(item):
        return True

    return False

def checkIfMenuHasSteak(menu):
    hasSteak = False

    for item in menu['data']:
        for meal in item['meals']:
            if(meal['meal_avail']):
                for genre in meal['genres']:
                    for item in genre['items']:
                        if isSteakItem(genre['genre_name'], item):
                            hasSteak = True
                            break

    return hasSteak


for menu in menus.find():
    unix_time = menu['data'][0]['date'] / 1000
    menutime = time.localtime(unix_time)
    date_string = time.strftime("%B %d, %Y",  menutime)
    hasSteak = checkIfMenuHasSteak(menu)
    print(date_string + ": " + str(hasSteak))

"""
for row in cur.fetchall():
    (genre, item) = row
    item_lower = item.lower()

    if "steak" in item_lower and validGenre(genre) and miscFlags(item):
        print(genre + ": " + item)
"""
