import string
import psycopg2

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

for row in cur.fetchall():
    (genre, item) = row
    item_lower = item.lower()

#    if "steak" in item_lower and validGenre(genre):
    if "steak" in item_lower:
        print(genre + ": " + item)
