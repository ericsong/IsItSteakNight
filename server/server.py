import string
import threading
import psycopg2
import re
import uuid
import os
from flask import Flask, render_template, send_from_directory, request, jsonify
from analyzer import isTonightSteakNight, getMenu
from send import sendConfirmationEmail

DB_PASS = os.environ['IISN_DB_PASS']

app = Flask(__name__, static_url_path='')

pattern = re.compile(".+@.+\..+")

try:
    conn = psycopg2.connect("host='localhost' dbname='isitsteaknight' user='iisn_admin' password='" + DB_PASS + "'")
except:
    print("I am unable to connect to the database")

status = {
    'isSteakNight': False
}

def validEmail(email):
    return pattern.match(email)

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
    cur = conn.cursor()
    token = request.args.get('token')

    values = {
        'token': token
    }

    #Execute query to check if subscription already exists
    select_template = string.Template("""
        SELECT email from "Subscriber" WHERE key='$token'
    """)
    select_query = select_template.substitute(values)
    cur.execute(select_query)
    result = cur.fetchone()

    if result is not None:
        update_template = string.Template("""
            UPDATE "Subscriber" SET verified=True WHERE key='$token'
        """)
        update_query = update_template.substitute(values)
        cur.execute(update_query)
        conn.commit()
        cur.close()
        return render_template('confirmed.html')
    else:
        cur.close()
        return render_template('unconfirmed.html')

@app.route('/unsubscribe/')
def unsubscribe():
    cur = conn.cursor()
    token = request.args.get('token')

    values = {
        'token': token
    }

    #Execute query to check if subscription already exists
    select_template = string.Template("""
        SELECT email from "Subscriber" WHERE key='$token'
    """)
    select_query = select_template.substitute(values)
    cur.execute(select_query)
    result = cur.fetchone()

    if result is not None:
        update_template = string.Template("""
            UPDATE "Subscriber" SET active=False WHERE key='$token'
        """)
        update_query = update_template.substitute(values)
        cur.execute(update_query)
        conn.commit()

        cur.close()
        return render_template('unsubscribe.html')
    else:
        cur.close()
        return render_template('unsubfailed.html')


@app.route('/subscribe', methods=['POST'])
def addSubscriber():
    cur = conn.cursor()
    email = request.form.get('email')
    query = request.form.get('query')
    query = query.lower()

    values = {
        'email': email,
        'query': query
    }

    if not validEmail(email):
        return jsonify({
            'message': "Invalid email",
            'status': "failure" 
        })

    #Execute query to check if subscription already exists
    select_template = string.Template("""
        SELECT id from "Subscription" WHERE subscriber='$email' AND query='$query'
    """)
    select_query = select_template.substitute(values)
    cur.execute(select_query)
    result = cur.fetchone()
    print(result)

    if result is not None:
        cur.close()
        return jsonify({
            'message': "You're already subscribed for this item!",
            'status': "failure"
        })

    #Execute query to check if subscriber already exists
    select_template = string.Template("""
        SELECT email from "Subscriber" WHERE email='$email'
    """)
    select_query = select_template.substitute(values)
    cur.execute(select_query)
    result = cur.fetchone()

    if result is None:
        values['key'] = uuid.uuid4()

        #Create new user
        insert_template = string.Template("""
            INSERT INTO "Subscriber" (email, key) VALUES ('$email', '$key')
        """)
        insert_query = insert_template.substitute(values)

        try:
            cur.execute(insert_query)
            conn.commit()

            sendConfirmationEmail(values)
        except Exception as e:
            print(e)
            print("create subscriber failed")

    insert_template = string.Template("""
        INSERT INTO "Subscription" (subscriber, query) VALUES ('$email', '$query')
    """)
    insert_query = insert_template.substitute(values)

    try:
        cur.execute(insert_query)
        conn.commit()
        cur.close()
        return jsonify({
            'message': "success",
            'status': "success"
        })
    except Exception as e:
        print(e)
        print("create subscription failed")

@app.route('/MenuData')
def sendMenuData():
    return jsonify(menu=getMenu())

if __name__ == '__main__':
    updateSteakCheck()
    set_interval(updateSteakCheck, 60)
    app.run(debug=True, host='0.0.0.0')
