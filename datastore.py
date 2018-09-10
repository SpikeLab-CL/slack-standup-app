from google.cloud import datastore
import datetime
import google.auth.credentials
from google.auth import app_engine

class DataStore(object):
    def __init__(self, credentials):
        """Datastore instace wrapper.
            Arguments:
                credentials: google.auth credentials, for development you can user appengine service account file.
        """
        self.client = datastore.Client(credentials=credentials)
    
    def retrieve_entry(self, key_id):
        """Get an entry from Datastore given the key_id
            Arguments:
                key_id: string with format SLACKUSERID_DATE.
            Returns:
                A Datastore entry with the daily standup of the user
        """
        key = self.client.key("Standup", key_id)
        entry = self.client.get(key)
        return entry
    
    def retrive_entry_by_msg_id(self, msg_id):
        """Get an entry from Datastore given a msg_id
            Arguments:
                msg_id: string with a slack message id.
            Returns:
                A Datastore entry with the daily standup from an user
        """
        query = self.client.query(kind="Standup")
        query.add_filter('answers.msg_id','=', msg_id)
        query_ = query.fetch()
        entry = None
        for ent in query_: #this alway is a single entry
           entry = ent
        return entry

    def store_daily_entry(self, entry, user, date):
        """Store a new daily standup entry in Datastore 
            Arguments:
                entry: dict with an empty daily standup.
                user: string with a slack user ID.
                date: string with the standup date.
        """
        key_id = "{0}_{1}".format(user,date)
        key = self.client.key("Standup", key_id)
        entity = datastore.Entity(key=key)
        entity.update(entry)
        self.client.put(entity)
    
    def update_standup(self, entry):
        """Update a standup entry in Datastore
            Arguments:
                entry: dict with the standup entry.
        """
        self.client.put(entry)

    def retrive_daily_team_meetup(self):
        """Get an entry from Datastore given a msg_id
            Arguments:
                msg_id: string with a slack message id.
            Returns:
                A Datastore entry with the daily standup from an user
        """
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        query = self.client.query(kind="Standup")
        query.add_filter('date','=', date)
        query_ = query.fetch()
        return query_
    
    def store_user(self, user):
        """Store in Datastore basic user information, only stored users 
            Arguments:
                user: dict with a slack user_id, team_id and channel_id.
        """
        key = self.client.key("Standup_user", user['user_id'])
        entity = datastore.Entity(key=key)
        entity.update({
            'user_id':user['user_id'],
            'team_id':user['team_id'],
            'channel_id':user['channel_id']
            })
        self.client.put(entity)
    
    def get_users(self):
        """Retrives the users information from Datastore
            Returns:
                users: dict with the user basic information
        """
        query = self.client.query(kind="Standup_user")
        query_ = query.fetch()
        users = list(map(lambda u: {'user_id':u['user_id'],
                                    'team_id':u['team_id'],
                                    'channel_id':u['channel_id']}, query_))
        return users

class GoogleServices(DataStore):    
    _credentials=None
    _datastore=None

    def __init__(self, credentials=None):
        if (credentials is not None and not isinstance(credentials,
            google.auth.credentials.Credentials)):
            raise TypeError("credentials must be of type "
                            "google.auth.credentials")
        self._credentials = (app_engine.Credentials() if not credentials 
                                                      else credentials)

    def datastore(self):
        if not self._datastore:
            self._datastore = DataStore(self._credentials) 
        return self._datastore