import hashlib
import pymongo
import random
from pymongo.errors import DuplicateKeyError, PyMongoError
import string
from blog.repo import errors

__author__ = 'tyerq'


class User:
    """
    Users DAO Class
    """

    def __init__(self, db):
        self.db = db
        self.coll = self.db.users

    def validate_user(self, username, passw):
        try:
            user = self.coll.find_one({'_id': username})
        except PyMongoError as err:
            raise errors.SomethingWentWrong(err)

        if not user:
            raise errors.EntryNotFound()

        hashed, salt = user['passw'].split(';')

        if user['passw'] != _make_hashed_passw(passw,salt):
            raise errors.WrongCredentials()

        return user

    def get_user(self, username):
        try:
            user = self.coll.find_one({'_id': username})
        except PyMongoError as err:
            raise errors.SomethingWentWrong(err)

        if not user:
            raise errors.EntryNotFound()

        return user

    def create_user(self, username, passw, name=None, email=None):

        user = {
            '_id': username,
            'passw': _make_hashed_passw(passw)
        }

        if name:
            user['name'] = name
        if email:
            user['email'] = email

        try:
            self.coll.insert_one(user)
        except DuplicateKeyError:
            raise errors.EntryExists()
        except PyMongoError as err:
            raise errors.SomethingWentWrong(err)


class Session:
    """
    Sessions DAO Class
    """
    def __init__(self, db):
        self.db = db
        self.sessions = self.db.sessions

    def start_session(self, username):

        _id = _make_salt(32)
        session = {'_id': _id, 'username': username}

        try:
            self.sessions.insert_one(session)
        except PyMongoError as err:
            raise errors.SomethingWentWrong(err)
        except DuplicateKeyError:
            print('session: got duplicate id. repeating...')
            return self.start_session(username)

        return session['_id']

    def end_session(self, session_id):

        if session_id is None:
            return

        try:
            self.sessions.remove_one({'_id': session_id})
        except PyMongoError as err:
            raise errors.SomethingWentWrong(err)

        return

    # get the username of the current session, or None if the session is not valid
    def get_username(self, session_id):

        try:
            session = self.sessions.find_one(session_id)
        except PyMongoError as err:
            raise errors.SomethingWentWrong(err)

        if not session:
            return None
        else:
            return session['username']


def _make_salt(length=8):
    salt = []
    for i in range(length):
        salt.append(random.choice(string.ascii_letters))

    return ''.join(salt)


def _make_hashed_passw(passw, salt=None):
    if not salt:
        salt = _make_salt()

    hashed = hashlib.sha256('{passw}{salt}'.format(passw=passw, salt=salt).encode('utf-8')).hexdigest()
    return '{hashed};{salt}'.format(hashed=hashed, salt=salt)


class db:

    _connection_string = "mongodb://localhost"
    _connection = pymongo.MongoClient(_connection_string)
    _db = _connection.pyramid_blog

    posts = None    # TODO define posts
    users = User(_db)
    sessions = Session(_db)