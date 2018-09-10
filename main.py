# -*- coding: utf-8 -*-

from flask import Flask
from flask import request
app = Flask(__name__)
import json
from slack import Slack
from google.oauth2 import service_account
from datastore import GoogleServices
import datetime
from utils import create_new_entry, datastore_key, process_stand_up, edit_stand_up, prepare_standup_message
from config import config

VERIFICATION_TOKEN = config['verification_token']
OAUTH_BOT_TOKEN = config['oauth_bot_token']

dev = False
credentials = None
if dev:
    SERVICE_ACCOUNT_FILE = config['account_service']
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE)

slack = Slack(OAUTH_BOT_TOKEN)
services = GoogleServices(credentials)

@app.route('/', methods = ['GET', 'POST'])
def main():
    """
    Main function that receives slack events, and do the main job.
    """
    data = json.loads(request.data)
    if 'challenge' in data:
        return data['challenge']
    else:
        token = data['token']
        if (token != VERIFICATION_TOKEN):
            return json.dumps({"error": "no valid token provided"})
        else:
            msg = slack.parse_message(data)
            if msg['type'] == 'new_entry':
                key = datastore_key(msg['user'])
                stand_up = services.datastore().retrieve_entry(key)
                if stand_up == None:
                    pass
                else:
                    updated, next_question = process_stand_up(stand_up, msg)
                    services.datastore().update_standup(updated)
                    if next_question == None:
                        slack.post_message("Todo ok por hoy!", msg['channel'])
                    else:
                        slack.post_message(next_question, msg['channel'])
            elif(msg['type'] == 'bot_msg'):
                pass #we dont do nothing if the bot post in the channel
            else:
                stand_up = services.datastore().retrive_entry_by_msg_id(msg['msg_id'])
                stand_up = edit_stand_up(stand_up, msg)
                services.datastore().update_standup(stand_up)
                slack.post_message("Se ha editado tu respuesta!", msg['channel'])
    return "ok"

@app.route('/postDaily', methods = ['GET'])
def dailyMessage():
    """
    Post a daily message in slack, asking to the users to responds the daily standup
    """
    users = services.datastore().get_users()
    msg = "Es hora del daily stand up, por favor responde: \
                         \n {0}".format(config['questions'][0])
    slack.post_all_user_msg(msg, users)
    return "ok"

@app.route('/createDailyEntry', methods=['GET'])
def createDailyEntry():
    """
        Create every day a new for workspace users in DataStore
    """
    users = services.datastore().get_users()
    for user in users:
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        entry = create_new_entry(user['user_id'],user['team_id'],user['channel_id'], date)
        services.datastore().store_daily_entry(entry, user['user_id'], date)
    return "ok"

@app.route('/addMembers', methods = ['GET'])
def addMembers():
    """
        Store the members basic info in DataStore, this is done every day at night so
        if there is new members in the workspace, they are add automatically to the standup 
        system.
    """
    members_list = slack.get_workspace_members()
    user_bot_channels = slack.get_user_bot_channels(members_list)
    for user in user_bot_channels:
        services.datastore().store_user(user)
    return "ok"

@app.route('/postDailyStandUp', methods = ['GET'])
def postDailyStandUp():
    """
        Post in slack the daily standup for all users in a specific channel
    """
    team_meet_up = services.datastore().retrive_daily_team_meetup()
    msg = prepare_standup_message(team_meet_up)
    slack.post_with_attachment(msg, config["channel"])
    return "ok"

@app.route('/warm', methods = ['GET'])
def warmUp():
    """
        Warm up the machine in AppEngine a few minutes before the daily standup
    """
    return "ok"

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)