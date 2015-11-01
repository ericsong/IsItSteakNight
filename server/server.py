import string
import threading
import psycopg2
from flask import Flask, render_template, send_from_directory, request, jsonify
from analyzer import isTonightSteakNight, getMenu

app = Flask(__name__, static_url_path='')

try:
    conn = psycopg2.connect("host='localhost' dbname='isitsteaknight' user='iisn_admin' password='abc123'")
except:
    print("I am unable to connect to the database")
cur = conn.cursor()

status = {
    'isSteakNight': False
}

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

@app.route('/subscribe', methods=['POST'])
def addSubscriber():
    email = request.form.get('email')
    query = request.form.get('query')
    values = {
        'email': email,
        'query': query
    }

    select_template = string.Template("""
        SELECT id from "Subscription" WHERE email='$email' AND query='$query'
    """)
    select_query = select_template.substitute(values)

    cur.execute(select_query)
    result = cur.fetchone()

    print(result)
    if result is not None:
        print('here')
        return jsonify(message="You're already subscribed for this item!")

    insert_template = string.Template("""
        INSERT INTO "Subscription" (email, query) VALUES ('$email', '$query')
    """)
    insert_query = insert_template.substitute(values)

    try:
        cur.execute(insert_query)
        conn.commit()
        return jsonify(message="success")
    except:
        print("create subscription failed")

@app.route('/MenuData')
def sendMenuData():
    return jsonify(menu=getMenu())

if __name__ == '__main__':
    updateSteakCheck()
    set_interval(updateSteakCheck, 60)
    app.run(debug=True, host='0.0.0.0')
