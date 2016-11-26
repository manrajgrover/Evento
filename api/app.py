import requests
import yaml
import json
import urlparse
from pprint import pprint
from flask import Flask, Response, render_template, request, redirect, url_for, session

app = Flask(__name__, template_folder = "../webapp", static_folder = "../webapp/dist")

CONFIG = None

with open("application.yml", 'r') as config:
    try:
        CONFIG = yaml.load(config)
    except yaml.YAMLError as error:
        print error

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', client_id = CONFIG['client_id'])

@app.route('/login')
def login():

    if (session.get('username') is not None) and (session.get('name') is not None):
        resp = {
            "error": False,
            "username": session['username'],
            "name": session['name']
        }

        return Response(response=json.dumps(resp),
                        status=200, \
                        mimetype="application/json")
    else:
        resp = {
            "error": True,
            "message": "Please authorize"
        }

        return Response(response = json.dumps(resp),
                        status = 401, \
                        mimetype = "application/json")

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

            auth_val = "token {token}".format(token = access_token)

            header = {
                "Authorization": auth_val
            }

            r = requests.get('https://api.github.com/user', headers = header)
            result = r.json()

            session['username'] = result['login']
            session['token'] = access_token
            session['name'] = result['name']
            
            return redirect(url_for('index'))
        else:
            resp = {
                "error": True,
                "message": "Permissions not given"
            }

            return Response(response=resp,
                            status=403, \
                            mimetype="application/json")
    else:
        resp = {
            "error": True,
            "message": "Unauthorized"
        }
        
        return Response(response = resp,
                        status = 401, \
                        mimetype = "application/json")

def getEventDetails(data):
    response = {}

    response['user_url'] = "https://github.com/{user}".format(user = data['actor']['login'])
    response['image'] = data['actor']['avatar_url']

    repository = data['repo']['name']

    response['repository'] = repository
    response['repository_url'] = "https://github.com/{repository}".format(repository = repository)
    response['timestamp'] = data['created_at']

    payload = data['payload']

    if data['type'] == "CommitCommentEvent":

        message = "Made a commit comment '{comment}'".format(comment = payload['comment']['body'])
        response['message'] = message
        response['message_url'] = payload['comment']['html_url']

    elif data['type'] == "CreateEvent":

        message = "Created a {ref_type}".format(ref_type = payload['ref_type'])
        response['message'] = message

    elif data['type'] == "DeleteEvent":

        message = "Deleted a {ref_type}".format(ref_type = payload['ref_type'])
        response['message'] = message

    elif data['type'] == "DeploymentEvent":

        message = "Deployed {ref} code to {environment}".format(ref = payload['deployment']['ref'], environment = payload['deployment']['environment'])
        response['message'] = message

    elif data['type'] == "DeploymentStatusEvent":
        pass

        # message = "Deployment status is {ref}".format(ref = payload['deployment']['ref'], environment = payload['deployment']['environment'])
        # response['message'] = message

    elif data['type'] == "DownloadEvent":
        response['message'] = "Lorem"
    elif data['type'] == "FollowEvent":
        response['message'] = "Lorem"
    elif data['type'] == "ForkEvent":
        response['message'] = "Lorem"
    elif data['type'] == "ForkApplyEvent":
        response['message'] = "Lorem"
    elif data['type'] == "GistEvent":
        response['message'] = "Lorem"
    elif data['type'] == "GollumEvent":
        response['message'] = "Lorem"
    elif data['type'] == "IssueCommentEvent":
        response['message'] = "Lorem"
    elif data['type'] == "IssuesEvent":
        response['message'] = "Lorem"
    elif data['type'] == "LabelEvent":
        response['message'] = "Lorem"
    elif data['type'] == "MemberEvent":
        response['message'] = "Lorem"
    elif data['type'] == "MembershipEvent":
        response['message'] = "Lorem"
    elif data['type'] == "MilestoneEvent":
        response['message'] = "Lorem"
    elif data['type'] == "PageBuildEvent":
        response['message'] = "Lorem"
    elif data['type'] == "PublicEvent":
        response['message'] = "Lorem"
    elif data['type'] == "PullRequestEvent":
        response['message'] = "Lorem"
    elif data['type'] == "PullRequestReviewEvent":
        response['message'] = "Lorem"
    elif data['type'] == "PullRequestReviewCommentEvent":
        response['message'] = "Lorem"
    elif data['type'] == "PushEvent":
        response['message'] = "Lorem"
    elif data['type'] == "ReleaseEvent":
        response['message'] = "Lorem"
    elif data['type'] == "RepositoryEvent":
        response['message'] = "Lorem"
    elif data['type'] == "StatusEvent":
        response['message'] = "Lorem"
    elif data['type'] == "TeamAddEvent":
        message = "{repository} was added to {team}".format(repository = payload['repository']['full_name'], team = payload['team']['name'])
        response['message'] = message
    elif data['type'] == "WatchEvent":
        message = "{action} watching the repository".format(action = payload['action'].title())
        response['message'] = message

    return response

@app.route('/events', methods = ['GET'])
def events():

    if (session.get('username') is not None) and (session.get('name') is not None):
        username = session['username']
        access_token = session['token']

        auth_val = "token {token}".format(token = access_token)

        header = {
            "Authorization": auth_val
        }

        page = request.args.get('page') if request.args.get('page') is not None else 1

        print page

        events_url = 'https://api.github.com/users/{username}/events?page={page}'.format(username = username, page = page)
        result = requests.get(events_url, headers = header)

        events = result.json()

        if result.status_code == requests.codes.ok and len(events):

            resp = []

            for event in events:
                resp.append(getEventDetails(event)) 
            
            return Response(response = json.dumps(resp),
                            status = 200, \
                            mimetype = "application/json")
        else:
            resp = {
                "error": True,
                "type": "END",
                "message": "No more to show"
            }

            return Response(response = json.dumps(resp),
                            status = 404, \
                            mimetype = "application/json")

    else:
        resp = {
            "error": True,
            "message": "Please authorize"
        }

        return Response(response = json.dumps(resp),
                        status = 401, \
                        mimetype = "application/json")

@app.route('/logout', methods = ['POST'])
def logout():
    session.pop('username', None)
    session.pop('name', None)
    session.pop('token', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.secret_key = "HelloWorld"
    app.run(debug = True)
