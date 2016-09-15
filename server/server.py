import string
import threading
import re
from dbinterface import *
from flask import Flask, render_template, send_from_directory, request, jsonify
from analyzer import isTonightSteakNight, getMenu
from send import sendConfirmationEmail, tellEricSomeoneSignedUp

app = Flask(__name__, static_url_path='')
app.debug = True

pattern = re.compile(".+@.+\..+")

MAX_NUM_ITEMS = 30

status = {
    'isSteakNight': False
}

def validEmail(email):
    return pattern.match(email)

def createSuccessMessage(msg, time=5):
    return jsonify({
        'message': msg,
        'status': "success",
        'time': time
    })

def createFailureMessage(msg, time=5):
    return jsonify({
        'message': msg,
        'status': "failure",
        'time': time
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
    successMessage = "Success!"

    # Check if email is somewhat valid (regex)
    if not validEmail(email):
        return createFailureMessage("Invalid email")

    # Check if subscription already exists
    try:
        subExists = subscriptionExists(email, query)
    except:
        return createFailureMessage("An error has occurred. Please try again later.")

    if subExists:
        return createFailureMessage("You're already subscribed for this item!")

    # Check if max number of items have been reached
    try:
        numItems = getNumberOfSubscriberItems(email)
        if numItems >= MAX_NUM_ITEMS:
            return createFailureMessage("You are already at the max number of items. If you want to track more than 30 items, please email eric.song@rutgers.edu", 10)
    except:
        return createFailureMessage("An error has occurred. Please try again later.")

    # Check if subscriber exists
    try:
        subscriber = getSubscriberByEmail(email)
    except:
        return createFailureMessage("An error has occurred. Please try again later.")

    if subscriber is None:
        # Create new user
        try:
            newUserKey = createSubscriber(email)
            tellEricSomeoneSignedUp(email)
        except:
            return createFailureMessage("An error has occurred. Please try again later.")

        successMessage = successMessage + " A confirmation email has been sent."
        sendConfirmationEmail(email, query, newUserKey)

    # Create subscription
    try:
        createSubscription(email, query)
    except:
        return createFailureMessage("An error has occurred. Please try again later.")

    return createSuccessMessage(successMessage)

@app.route('/MenuData')
def sendMenuData():
    return jsonify(menu=getMenu())

updateSteakCheck()
set_interval(updateSteakCheck, 60)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
