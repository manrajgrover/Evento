import requests
import yaml
import json
import urlparse
from pprint import pprint
from flask import Flask, Response, render_template, request, redirect, url_for, session

app = Flask(__name__, template_folder="../webapp",
            static_folder="../webapp/dist")

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


@app.route('/login', methods=['GET'])
def login():

    if ((session.get('username') is not None) and
            (session.get('name') is not None)):
        resp = {
            "error": False,
            "username": session['username'],
            "name": session['name']
        }

        return Response(response=json.dumps(resp),
                        status=200,
                        mimetype="application/json")
    else:
        resp = {
            "error": True,
            "message": "Please authorize"
        }

        return Response(response=json.dumps(resp),
                        status=401,
                        mimetype="application/json")


@app.route('/callback', methods=['GET'])
def callback():
    code = request.args.get("code")
    response = requests.post("https://github.com/login/oauth/access_token",
                             data={
                                 'client_id': CONFIG['client_id'],
                                 'client_secret': CONFIG['client_secret'],
                                 'code': code
                             }
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

            return redirect(url_for('index'))
        else:
            resp = {
                "error": True,
                "message": "Permissions not given"
            }

            return Response(response=resp,
                            status=403,
                            mimetype="application/json")
    else:
        resp = {
            "error": True,
            "message": "Unauthorized"
        }

        return Response(response=resp,
                        status=401,
                        mimetype="application/json")


def getEventDetails(data):
    response = {}

    response[
        'user_url'] = "https://github.com/{user}".format(user=data['actor']['login'])
    response['image'] = data['actor']['avatar_url']

    repository = data['repo']['name']

    response['repository'] = repository
    response[
        'repository_url'] = "https://github.com/{repository}".format(repository=repository)
    response['timestamp'] = data['created_at']

    try:
        payload = data['payload']
    except KeyError:
        payload = None

    if data['type'] == "CommitCommentEvent":

        message = "Made a commit comment '{comment}'".format(
            comment=payload['comment']['body'])
        response['message'] = message
        response['message_url'] = payload['comment']['html_url']

    elif data['type'] == "CreateEvent":

        message = "Created a {ref_type}".format(ref_type=payload['ref_type'])
        response['message'] = message

    elif data['type'] == "DeleteEvent":

        message = "Deleted a {ref_type}".format(ref_type=payload['ref_type'])
        response['message'] = message

    elif data['type'] == "DeploymentEvent":

        message = "Deployed {ref} code to {environment}".format(
            ref=payload['deployment']['ref'], environment=payload['deployment']['environment'])
        response['message'] = message

    elif data['type'] == "DeploymentStatusEvent":
        message = "Deployed {ref} to {environment} with {status}".format(ref=payload['deployment'][
                                                                         'ref'], environment=payload['deployment']['environment'], status=payload['deployment_status']['state'])
        response['message'] = message

    elif data['type'] == "DownloadEvent":
        message = "Download event created with file name '{file_name}'".format(
            file_name=payload['download']['name'])
        response['message'] = message
    elif data['type'] == "FollowEvent":
        message = "Followed user {username}".format(
            username=payload['target']['login'])
        response['message'] = message
    elif data['type'] == "ForkEvent":
        message = "Forked a repository to {repo_name}".format(
            repo_name=payload['forkee']['full_name'])
        response['message'] = message
    elif data['type'] == "ForkApplyEvent":
        message = "Patch applied in the Fork Queue on branch {branch}".format(
            branch=payload['head'])
        response['message'] = message
    elif data['type'] == "GistEvent":
        message = "{action} a gist".format(action=payload['action'])
        response['message'] = message
        response['message_url'] = payload['gist']['html_url']
    elif data['type'] == "GollumEvent":
        response['message'] = "Created/Updated a Wiki Page"
    elif data['type'] == "IssueCommentEvent":
        message = "{action} a comment on issue #{number} with title '{title}'".format(
            action=payload['action'].title(), number=payload['issue']['number'], title=payload['issue']['title'])
        response['message'] = message
        response['message_url'] = payload['comment']['html_url']
    elif data['type'] == "IssuesEvent":
        message = "{action} an issue #{number} with title '{title}'".format(action=payload[
                                                                            'action'].title(), number=payload['issue']['number'], title=payload['issue']['title'])
        response['message'] = message
        response['message_url'] = payload['issue']['html_url']
    elif data['type'] == "LabelEvent":
        message = "{action} a label named {label_name}".format(
            action=payload['action'].title(), label_name=payload['label']['name'])
        response['message'] = message
    elif data['type'] == "MemberEvent":
        response['message'] = "Added to repository as a collaborator"
    elif data['type'] == "MembershipEvent":
        action = payload['action']

        if action == "added":
            message = "{name} was {action} to team {team_name}".format(
                name=payload['member']['login'], action=action, team_name=payload['team']['name'])
        else:
            message = "{name} was {action} from team {team_name}".format(
                name=payload['member']['login'], action=action, team_name=payload['team']['name'])
        response['message'] = message
    elif data['type'] == "MilestoneEvent":
        message = "{action} a milestone #{number}".format(
            action=payload['action'], number=payload['milestone']['number'])
        response['message'] = message
        response['message_url'] = payload['milestone']['html_url']
    elif data['type'] == "PageBuildEvent":
        if payload['build']['error']['message'] is not None:
            result = "Error occured with message: {message}".format(
                message=payload['build']['error']['message'])
        else:
            result = "Build was successful."
        message = "Tried building Github pages. {result}".format(result=result)
        response['message'] = message
    elif data['type'] == "PublicEvent":
        response['message'] = "Open Sourced the repository"
    elif data['type'] == "PullRequestEvent":
        message = "{action} pull request #{number}".format(
            action=payload['action'].title(), number=payload['number'])
        response['message'] = message
        response['message_url'] = payload['pull_request']['html_url']
    elif data['type'] == "PullRequestReviewEvent":
        message = "{action} a pull request review on #{number}".format(
            action=payload['action'].title(), number=payload['pull_request']['number'])
        response['message'] = message
        response['message_url'] = payload['review']['html_url']
    elif data['type'] == "PullRequestReviewCommentEvent":
        message = "{action} a comment on pull request #{number}".format(
            action=payload['action'].title(), number=payload['pull_request']['number'])
        response['message'] = message
        response['message_url'] = payload['comment']['html_url']
    elif data['type'] == "PushEvent":
        message = "Pushed {size} commit(s) to the repository".format(
            size=payload['size'])
        response['message'] = message
    elif data['type'] == "ReleaseEvent":
        message = "{action} the repository with tag {tag_name}".format(
            action=payload['action'], tag_name=payload['release']['tag_name'])
        response['message'] = message
    elif data['type'] == "RepositoryEvent":
        message = "{action} the repository".format(action=payload['action'])
        response['message'] = message
    elif data['type'] == "StatusEvent":
        message = "Status of commit with sha {sha} changed to {status}".format(
            sha=payload['sha'], status=payload['state'])
        response['message'] = message
    elif data['type'] == "TeamAddEvent":
        message = "{repository} was added to {team}".format(
            repository=payload['repository']['full_name'], team=payload['team']['name'])
        response['message'] = message
    elif data['type'] == "WatchEvent":
        message = "{action} watching the repository".format(
            action=payload['action'].title())
        response['message'] = message

    return response


@app.route('/events', methods=['GET'])
def events():

    if (session.get('username') is not None) and (session.get('name') is not None):
        username = session['username']
        access_token = session['token']

        auth_val = "token {token}".format(token=access_token)

        header = {
            "Authorization": auth_val
        }

        page = request.args.get('page') if request.args.get(
            'page') is not None else 1

        print page

        events_url = 'https://api.github.com/users/{username}/events?page={page}'.format(
            username=username, page=page)
        result = requests.get(events_url, headers=header)

        events = result.json()

        if result.status_code == requests.codes.ok and len(events):

            resp = []

            for event in events:
                resp.append(getEventDetails(event))

            return Response(response=json.dumps(resp),
                            status=200,
                            mimetype="application/json")
        else:
            resp = {
                "error": True,
                "type": "END",
                "message": "No more to show"
            }

            return Response(response=json.dumps(resp),
                            status=404,
                            mimetype="application/json")

    else:
        resp = {
            "error": True,
            "message": "Please authorize"
        }

        return Response(response=json.dumps(resp),
                        status=401,
                        mimetype="application/json")


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    session.pop('name', None)
    session.pop('token', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.secret_key = CONFIG['app_secret_key']
    app.run(debug=True)
