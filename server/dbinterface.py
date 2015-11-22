import psycopg2
import uuid
import string
import os
from raven import Client as RavenClient

DB_PASS = os.environ['IISN_DB_PASS']

raven_client = RavenClient(os.environ['SENTRY_DSN'])

try:
    conn = psycopg2.connect("host='localhost' dbname='isitsteaknight' user='iisn_admin' password='" + DB_PASS + "'")
except:
    print("I am unable to connect to the database")

status = {
    'isSteakNight': False
}

def tryCatchSelectOneQuery(query):
    cur = conn.cursor()

    try:
        cur.execute(query)
        doc = cur.fetchone()

        cur.close()
        return doc
    except:
        raven_client.user_context({
            'query': query
        })
        raven_client.captureMessage('PostgreSQL SELECT query failed')

        cur.close()

        raise ValueError("PostgreSQL SELECT query failed")

def tryCatchInsertQuery(query):
    cur = conn.cursor()

    try:
        cur.execute(query)
        conn.commit()
        cur.close()

        return True
    except Exception as e:
        raven_client.user_context({
            'query': query
        })
        raven_client.captureMessage('PostgreSQL INSERT query failed')

        conn.rollback()
        cur.close()
        
        raise ValueError("PostgreSQL INSERT query failed")

def getSubscription(email, query):
    """ Returns subscription if exists """

    values = {
        'email': email,
        'query': query
    }

    select_template = string.Template("""
        SELECT id from "Subscription" WHERE subscriber='$email' AND query='$query'
    """)
    select_query = select_template.substitute(values)

    try:
        return tryCatchSelectOneQuery(select_query)
    except:
        raise ValueError("Get subscription failed")

def getSubscriberByKey(key):
    """ Returns subscriber if exists """

    values = {
        'key': key
    }

    select_template = string.Template("""
        SELECT email from "Subscriber" WHERE key='$key'
    """)
    select_query = select_template.substitute(values)

    try:
        return tryCatchSelectOneQuery(select_query)
    except:
        raise ValueError("Get subscriber by key failed")

def getSubscriberByEmail(email):
    """ Returns subscriber if exists """

    values = {
        'email': email
    }

    select_template = string.Template("""
        SELECT email from "Subscriber" WHERE email='$email'
    """)
    select_query = select_template.substitute(values)

    try:
        return tryCatchSelectOneQuery(select_query)
    except:
        raise ValueError("Get subscriber by email failed")

def getNumberOfSubscriberItems(email):
    """ Return number of items subscriber with email of `email` currently is tracking """

def subscriptionExists(email, query):
    """ Return if subscription exists or not """

    try:
        result = getSubscription(email, query)
    except:
        raise ValueError("Checking for subscription failed")

    if result is None:
        return False
    else:
        return True

def subscriberExists(key):
    """ Return if subscriber exists or not """

    try:
        result = getSubscriberByKey(key)
    except:
        raise ValueError("Checking for subscriber failed")

    if result is None:
        return False
    else:
        return True

def createSubscriber(email):
    """ Create a subscriber and add to database. Return his unique key """

    values = {
        'email': email,
        'key': uuid.uuid4(),
    }

    insert_template = string.Template("""
        INSERT INTO "Subscriber" (email, key) VALUES ('$email', '$key')
    """)
    insert_query = insert_template.substitute(values)

    try:
        result = tryCatchInsertQuery(insert_query)
    except:
        raise ValueError("Create subscriber failed")

    return values['key']

def createSubscription(email, query):
    """ Create a subscription and add to database. Return unique id if successful """

    values = {
        'email':  email,
        'query': query
    }

    insert_template = string.Template("""
        INSERT INTO "Subscription" (subscriber, query) VALUES ('$email', '$query')
    """)
    insert_query = insert_template.substitute(values)
    result = tryCatchInsertQuery(insert_query)

    return result

def updateSubscriberConfirmStatus(key, status):
    """ Set subscriber with key of key as confirmed """

    values = {
        'key': key,
        'status': status
    }

    update_template = string.Template("""
        UPDATE "Subscriber" SET verified=$status WHERE key='$token'
    """)
    update_query = update_template.substitute(values)
    return tryCatchInsertQuery(update_query)


