import threading
from flask import Flask
from analyzer import isTonightSteakNight

app = Flask(__name__)

isSteakNight = False

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

def updateSteakCheck():
    isSteakNight = isTonightSteakNight()

@app.route('/')
def root():
    return str(isSteakNight)

if __name__ == '__main__':
    updateSteakCheck()
    set_interval(updateSteakCheck, 60)
    app.run(host='0.0.0.0')
