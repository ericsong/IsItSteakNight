import string
import psycopg2
from pymongo import MongoClient

client = MongoClient
client = MongoClient('127.0.0.1', 27017)
db = client.isitsteaknight

menus = db.menus

try:
    conn = psycopg2.connect("host='localhost' dbname='isitsteaknight' user='iisn_admin' password='abc123'")
except:
    print("I am unable to connect to the database")

cur = conn.cursor()

def insertGenre(genre, dininghall):
    values = {
        'genre_name': genre.replace("'", "''"),
        'id': dininghall
    }

    insert_str_template = string.Template("""
    INSERT INTO "Genre" (name, dininghall) SELECT '$genre_name', $id WHERE NOT EXISTS ( SELECT id FROM "Genre" WHERE name='$genre_name' AND dininghall=$id )
    """)
    insert_str = insert_str_template.substitute(values)

    try:
        cur.execute(insert_str)
        conn.commit()
    except:
        print("insert genre failed")

    select_template = string.Template("""
    SELECT id from "Genre" WHERE name='$genre_name' AND dininghall=$id
    """)
    select_query = select_template.substitute(values)
    cur.execute(select_query)

    return cur.fetchall()[0][0]

def insertItem(item, genre):
    values = {
        'item': item.replace("'", "''"),
        'id': genre
    }

    insert_str_template = string.Template("""
    INSERT INTO "Item" (name, genre) SELECT '$item', $id WHERE NOT EXISTS ( SELECT id FROM "Item" WHERE name='$item' AND genre=$id )
    """)
    insert_str = insert_str_template.substitute(values)

    try:
        cur.execute(insert_str)
        conn.commit()
    except:
        print("insert genre failed")

    select_template = string.Template("""
    SELECT id from "Item" WHERE name='$item' AND genre=$id
    """)
    select_query = select_template.substitute(values)
    cur.execute(select_query)

    return cur.fetchall()[0][0]

for menu in menus.find():
    for item in menu['data']:
        location_name = item['location_name']
        cur.execute("SELECT id from \"DiningHall\" WHERE name='" + location_name + "'")
        dininghall_id = cur.fetchall()[0][0]

        for meal in item['meals']:
            if(meal['meal_avail']):
                for genre in meal['genres']:
                    genre_name = genre['genre_name']

                    genre_id = insertGenre(genre_name, dininghall_id)
                    print(genre_id)

                    for item in genre['items']:
                        item_id = insertItem(item, genre_id)
                        print('item: ' + str(item_id))
client.close()
