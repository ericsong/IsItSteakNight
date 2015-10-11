from flask import Flask
from analyzer import isTonightSteakNight

app = Flask(__name__)

@app.route('/')
def root():
    return str(isTonightSteakNight())

if __name__ == '__main__':
    app.run()
