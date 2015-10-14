import threading
from flask import Flask, render_template
from analyzer import isTonightSteakNight

app = Flask(__name__)

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

@app.route('/')
def root():
    if status['isSteakNight']:
        display_str = "YES"
    else:
        display_str = "NO"

    return render_template('home.html', isSteakNight=display_str, items=status['items'])

if __name__ == '__main__':
    updateSteakCheck()
    set_interval(updateSteakCheck, 60)
    app.run(debug=True, host='0.0.0.0')
