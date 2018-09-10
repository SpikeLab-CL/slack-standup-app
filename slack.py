# -*- coding: utf-8 -*-
import requests
import json

class Slack():
    """Slack API wrapper
        Arguments:
            bot_token: string with the slack bot token.
    """    
    def __init__(self, bot_token):
        self.bot_token = bot_token
    
    def parse_message(self, message):
        """Parse and get the relevant info from a message from slack
            Arguments:
                message: dict with a slack event.
            Returns:
                msg: dict with the event relevant information.
        """    
        msg = {}
        #check if is a edited msg
        msg['time'] = message['event_time']
        msg['team_id'] = message['team_id'] 
        msg['channel'] = message['event']['channel']
        if('subtype' in message['event']):
            if(message['event']['subtype'] == 'message_changed'):
                msg['text'] = message['event']['message']['text']
                msg['user'] = message['event']['message']['user']
                msg['msg_id'] = message['event']['message']['client_msg_id']
                msg['type'] = "edit_msg"
            elif(message['event']['subtype'] == 'me_message'):
                msg['type'] = "bot_msg"
        else:
            msg['text'] = message['event']['text']
            msg['user'] = message['event']['user']
            msg['msg_id'] = message['event']['client_msg_id']
            msg['type'] = 'new_entry'
        return msg

    def get_workspace_members(self):
        """Retrieves information from the users in the installed bot workspace
            Returns:
                members: dict with active/non-bot workspace members.
        """  
        url = "https://slack.com/api/users.list"
        payload = {'token': self.bot_token }
        r = requests.get(url, params=payload)
        members = json.loads(r.text)
        members = members['members']
        members = map(lambda x: {'id':x['id'], 
                                 'is_bot':x['is_bot'],
                                 'team_id':x['team_id'],
                                 'is_app_user':x['is_app_user'],
                                 'deleted':x['deleted']},
                                 members)
        members = filter(lambda x: (x['is_bot'] == False  \
                                   and x['is_app_user'] == False \
                                   and x['deleted'] == False
                                   and x['id'] != "USLACKBOT"),
                                members)
        return members
    
    def get_user_bot_channels(self, members):
        """Open a conversation between bot and a list of given users and retrives the channel id.
            Returns:
                channnels: dict with the users ids, team_id, and channel_id,
                           where the channel_id is the channel between workspace members and the bot
        """  
        url = "https://slack.com/api/im.open"
        channels = []
        for user in members:
            payload = {'token': self.bot_token, 'user':user['id'] }
            r = requests.get(url, params=payload)
            r = json.loads(r.text)
            channels.append({'user_id':user['id'],'team_id':user['team_id'],'channel_id':r['channel']['id']})
        return channels

    def post_message(self, msg, channel):
        """Post a message in a slack channel.
           Arguments:
                msg: dict with an slack formated message.
                channel: string with the channel id in wich the message is posted.
        """  
        url = "https://slack.com/api/chat.meMessage"
        payload = { 'token': self.bot_token, 'channel':channel,'text':msg, 'as_user':False }
        r = requests.post(url, params=payload)


    def post_with_attachment(self, msg, channel):
        """Open a conversation between bot and a list of given users and retrives the channel id.
           Arguments:
                msg: dict with an slack formated message.
                channel: string with the channel id in wich the message is posted.
        """  
        url = "https://slack.com/api/chat.postMessage"
        msg['channel'] = channel
        msg['as_user'] = False
        headers = {'Content-Type':'application/json', 'Authorization': "Bearer {0}".format(self.bot_token)}
        msg = json.dumps(msg)
        r = requests.post(url, headers=headers, data=msg)
        print(r.content)
         
    def post_all_user_msg(self, msg, users):
        """Post a message in a list of users.
           Arguments:
                msg: dict with an slack formated message.
                users: dict with users information.
        """  
        users_ = users
        for user in users_:
            self.post_message(msg, user['channel_id'])