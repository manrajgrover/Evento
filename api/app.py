import requests
import yaml
import json
from flask import Flask, Response, render_template

app = Flask(__name__, template_folder="../webapp", static_folder="../webapp/dist")

CONFIG = None

with open("application.yml", 'r') as config:
    try:
        CONFIG = yaml.load(config)
    except yaml.YAMLError as exc:
        print exc 

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    data = {
        "error": True
    }

    resp = Response(response=json.dumps(data),
                    status=200, \
                    mimetype="application/json")
    return resp

@app.route('/callback')
def callback():
    pass

@app.route('/logout')
def logout():
    pass

if __name__ == '__main__':
    app.run(debug=True)
