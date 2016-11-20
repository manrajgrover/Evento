import requests
import yaml
import json
import urlparse
from pprint import pprint
from flask import Flask, Response, render_template, request, redirect, url_for, session

app = Flask(__name__, template_folder="../webapp", static_folder="../webapp/dist")

CONFIG = None

with open("application.yml", 'r') as config:
    try:
        CONFIG = yaml.load(config)
    except yaml.YAMLError as error:
        print error

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', client_id=CONFIG['client_id'])

@app.route('/login')
def login():
    

    resp = {
        "username": session['username'],
        "name": session['name']
    }

@app.route('/callback')
def callback():
    code = request.args.get("code")
    response = requests.post("https://github.com/login/oauth/access_token",
                            data = {
                                'client_id': CONFIG['client_id'],
                                'client_secret': CONFIG['client_secret'],
                                'code': code
                                } \
                            )

    if response.status_code == requests.codes.ok:

        result = urlparse.parse_qs(response.text)
        access_token = result['access_token'][0]
        scope = result['scope']

        if 'repo,user' in scope:

            auth_val = "token {token}".format(token=access_token)

            header = {
                "Authorization": auth_val
            }

            r = requests.get('https://api.github.com/user', headers=header)
            result = r.json()

            session['username'] = result['login']
            session['token'] = access_token
            session['name'] = result['name']

            # events_url = 'https://api.github.com/users/{username}/events'.format(username=username)
            # events = requests.get(events_url, params=params)
            
            return redirect(url_for('index'))
        else:
            pass
    else:
        pass
    return "hello world"

@app.route('/logout')
def logout():
    pass

if __name__ == '__main__':
    app.secret_key = "HelloWorld"
    app.run(debug=True)
