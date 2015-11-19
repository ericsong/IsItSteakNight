import string
import threading
import psycopg2
import re
import uuid
import os
from raven import Client as RavenClient
from flask import Flask, render_template, send_from_directory, request, jsonify
from analyzer import isTonightSteakNight, getMenu
from send import sendConfirmationEmail

DB_PASS = os.environ['IISN_DB_PASS']

raven_client = RavenClient(os.environ['SENTRY_DSN'])

app = Flask(__name__, static_url_path='')
app.debug = True

pattern = re.compile(".+@.+\..+")

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
        return None

def tryCatchInsertQuery(query):
    cur = conn.cursor()

    try:
        cur.execute(query)
        conn.commit()
        cur.close()

        return True
    except:
        raven_client.user_context({
            'query': query
        })
        raven_client.captureMessage('PostgreSQL INSERT query failed')

        cur.close()
        
        raise ValueError("PostgreSQL INSERT query failed")
        return None

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
    return tryCatchSelectOneQuery(select_query)

def getSubscriberByKey(key):
    """ Returns subscriber if exists """
    values = {
        'key': key
    }
    select_template = string.Template("""
        SELECT email from "Subscriber" WHERE key='$key'
    """)
    select_query = select_template.substitute(values)
    return tryCatchSelectOneQuery(cur, select_query)

def subscriptionExists(email, query):
    """ Return if subscription exists or not """
    result = getSubscription(email, query)
    
    if result is not None:
        return True
    else:
        return False

def subscriberExists(key):
    """ Return if subscriber exists or not """
    result = getSubscriberByKey(key)

    if result is not None:
        return True
    else:
        return False

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
    result = tryCatchInsertQuery(insert_query)

    if result is not None:
        return values['key']
    else:
        return None

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
    result = tryCatchInsertQuery(cur, insert_query)

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
    return tryCatchInsertQuery(cur, update_query)

def validEmail(email):
    return pattern.match(email)

def successMessage(msg):
    return jsonify({
        'message': msg,
        'status': "success"
    })

def failureMessage(msg):
    return jsonify({
        'message': msg,
        'status': "failure"
    })

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.daemon = True
    t.start()
    return t

def updateSteakCheck():
    isSteakNight, items = isTonightSteakNight()
    status['isSteakNight'] = isSteakNight
    status['items'] = items

@app.route('/static/<path:path>')
def send_static(path):
      return send_from_directory('static', path)

@app.route('/')
def root():
    if status['isSteakNight']:
        display_str = "YES"
    else:
        display_str = "NO"
    
    return render_template('home.html', isSteakNight=display_str, items=status['items'])

@app.route('/ConfirmSubscriber/')
def confirmSubscriber():
    token = request.args.get('token')

    # Check if key is linked to a user
    try:
        if subscriberExists(token) and updateSubscriberConfirmStatus(token, True):
            return render_template('confirmed.html')
        else:
            return render_template('unconfirmed.html')
    except:
        return render_template('unconfirmed.html')

@app.route('/unsubscribe/')
def unsubscribe():
    token = request.args.get('token')

    # Check if key is linked to a user
    try:
        if subscriberExists(token) and updateSubscriberConfirmStatus(token, False):
            return render_template('unsubscribe.html')
        else:
            return render_template('unsubfailed.html')
    except:
        return render_template('unsubfailed.html')

@app.route('/subscribe', methods=['POST'])
def addSubscriber():
    email = request.form.get('email')
    query = request.form.get('query').lower()

    # Check if email is somewhat valid (regex)
    if not validEmail(email):
        return failureMessage("Invalid email")

    # Check if subscription already exists
    try:
        if subscriptionExists(email, query):
            return failureMessaeg("You're already subscribed for this item!")
    except:
        return failureMessage("An error has occurred. Please try again later.")

    #Execute query to check if subscriber already exists
    select_template = string.Template("""
        SELECT email from "Subscriber" WHERE email='$email'
    """)
    select_query = select_template.substitute(values)
    result = tryCatchSelectOneQuery(cur, select_query)

    if result == "error":
        return jsonify({
            'message': "An error has occurred. Please try again later.",
            'status': "failure"
        })

    if result is None:
        # Create new user
        newUserKey = createSubscriber(email)

        if newUserKey is None:
            return jsonify({
                'message': "An error has occurred. Please try again later.",
                'status': "failure"
            })
        else:
            sendConfirmationEmail(values)

    # Create subscription
    subscriptionId = createSubscription(email, query)
    if subscriptionId is None:
        return jsonify({
            'message': "An error has occurred. Please try again later.",
            'status': "failure"
        })

    return jsonify({
        'message': "success",
        'status': "success"
    })

@app.route('/MenuData')
def sendMenuData():
    return jsonify(menu=getMenu())

updateSteakCheck()
set_interval(updateSteakCheck, 60)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
