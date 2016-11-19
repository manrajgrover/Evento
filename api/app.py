import requests
import yaml
from flask import Flask, render_template

app = Flask(__name__, template_folder="../webapp", static_folder="../webapp/dist")

with open("application.yaml", 'r') as config:
    try:
        print yaml.load(config)
    except yaml.YAMLError as exc:
        print exc 

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    pass

@app.route('/callback')
def callback():
    pass

@app.route('/logout')
def logout():
    pass

if __name__ == '__main__':
    app.run(debug=True)
