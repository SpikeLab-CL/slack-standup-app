# -*- coding: utf-8 -*-
from config import config
import datetime

def create_new_entry(user_id, team_id, channel_id, date):
    """Get an entry from Datastore given the key_id
        Arguments:
            user_id: string with a slack user ID.
            team_id: string with a slack team ID.
            channel_id: string with a slack channel ID.
            date: string with date in format yyyy-mm-dd
        Returns:
            dict: with user information, and daily standup questions with and empty response
    """    
    return {
        'user_id':user_id,
        'team_id':team_id,
        'channel_id':channel_id,
        'date': date,
        'answers': list(map(lambda question: {
            'question': question,
            'response': None,
            'created_at':None,
            'msg_id':None,
            'answered':False
        }, config['questions']))
    }

def datastore_key(user):
    """Creates a new key (in string) for a datastore entity
        Arguments:
            userd: string with a slack user ID.
        Returns:
            key: a new key used like id for a datastore entity
                 example: SLACKUSERID_YYYY-MM-DD
    """ 
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    return "{0}_{1}".format(user, date)

def process_stand_up(stand_up, answer):
    """Add the an answer to a daily standup, and retrieves the next unanswered question 
        Arguments:
            answer: dict with the awnser info (text, user_id, slack message id, etc).
        Returns:
            standup: dict with a updated standup info.
            next_: string with the next unanswered question 
    """
    next_ = None
    for answ in stand_up['answers']:
        if answ['answered'] == False:
            answ['answered'] = True
            answ['created_at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            answ['msg_id'] = answer['msg_id']
            answ['response'] = answer['text']
            break

    for answ in stand_up['answers']:
        if answ['answered'] == False:
            next_ = answ['question']
            break
    return stand_up, next_

def edit_stand_up(stand_up, answer):
    """Updates the answer of an edited message.
        Arguments:
            answer: dict with the awnser info (text, user_id, slack message id, etc).
        Returns:
            standup: dict with a updated standup info.
    """
    for answ in stand_up['answers']:
        if answ['msg_id'] == answer['msg_id']:
            answ['response'] == answer['text']
            answ['created_at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return stand_up

def prepare_standup_message(daily_standup):
    """Given all team standup entries, format the message for slack.
        Arguments:
            daily_standup: dict with all standup answers
        Returns:
            msg: dict with a slack formated message.
    """
    msg = {
        "text":"Hey equipo!, aquí está el daily standup :coffee: :coffee: :coffee:"
    }
    standup = list(map(lambda x: {
        "color": "#36a64f",
        "text": "<@{0}>".format(x['user_id']),
        "fields": list(map(lambda y: {
                    "title": y['question'],
                    "value": y['response'],
                    "short": False
        }, x['answers']))
    },daily_standup))
    msg['attachments'] = standup
    return msg
