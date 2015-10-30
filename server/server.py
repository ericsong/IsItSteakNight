import threading
from flask import Flask, render_template, send_from_directory, request, jsonify
from analyzer import isTonightSteakNight, getMenu

app = Flask(__name__, static_url_path='')

status = {
    'isSteakNight': False
}

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
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

    print(email, query)
    return jsonify(message="success")

@app.route('/MenuData')
def sendMenuData():
    return jsonify(menu=getMenu())

if __name__ == '__main__':
    updateSteakCheck()
    set_interval(updateSteakCheck, 60)
    app.run(debug=True, host='0.0.0.0')
