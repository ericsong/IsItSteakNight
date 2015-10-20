import time
import string
import json
import requests
import sys
import psycopg2
import pymongo
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client.isitsteaknight

menus = db.menus

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
    if "philly" in item_lower or "tuna" in item_lower or "sandwich" in item_lower:
        return False

    return True

def isSteakItem(genre, item):
    item_lower = item.lower()
    if "steak" in item_lower and validGenre(genre) and miscFlags(item):
        return True

    return False

def checkIfMenuHasSteak(menu):
    hasSteak = False
    items = []

    for dininghall in menu:
        for meal in dininghall['meals']:
            if(meal['meal_avail']):
                for genre in meal['genres']:
                    for item in genre['items']:
                        if isSteakItem(genre['genre_name'], item):
                            hasSteak = True
                            items.append({
                                'dininghall': dininghall['location_name'],
                                'genre': genre['genre_name'],
                                'item': item
                            })

    #return items here
    return (hasSteak, items)

def isTonightSteakNight(queryDatabase=False):
    if queryDatabase:
        latestMenu = menus.find().sort([("time", pymongo.DESCENDING)])[0]['data']
    else:
        r = requests.get('https://rumobile.rutgers.edu/1/rutgers-dining.txt')
        latestMenu = json.loads(r.text)

    unix_time = latestMenu[0]['date'] / 1000
    menutime = time.localtime(unix_time)
    date_string = time.strftime("%B %d, %Y",  menutime)
    return checkIfMenuHasSteak(latestMenu)
