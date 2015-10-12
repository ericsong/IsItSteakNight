import threading
from flask import Flask, render_template
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
    return render_template('home.html', isSteakNight=isSteakNight)

if __name__ == '__main__':
    updateSteakCheck()
    set_interval(updateSteakCheck, 60)
    app.run(debug=True)
