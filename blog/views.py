from pyramid.httpexceptions import HTTPFound, HTTPUnauthorized

from pyramid.view import view_config

from blog.repo import errors
from blog.repo.mongodb import db
from blog.utils import validate_signup


@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    return {}


@view_config(route_name='hello', renderer='templates/hello.pt')
def hello_view(request):
    session_id = request.cookies.get('session')
    username = db.sessions.get_username(session_id)

    if not username:
        print("no previous session. redirecting to /signup")
        return HTTPFound(location='/signup')
    else:
        try:
            user = db.users.get_user(username)
        except errors.EntryNotFound:
            return HTTPUnauthorized(detail='Your session seems to be corrupted. Try restarting your session.')
        else:
            return {
                'name': user['name'] if 'name' in user else username,
                'username': username
            }


@view_config(route_name='signup', renderer='templates/signup.pt', request_method='GET')
def signup_get(request):
    return {
        'errors': [],
        'username': '',
        'name': '',
        'email': ''
    }


@view_config(route_name='signup', renderer='templates/signup.pt', request_method='POST')
def signup_post(request):
    res = validate_signup(request.params['username'], request.params['passw'], request.params['repeat'],
                          request.params['name'], request.params['email'])
    if res['ok']:
        try:
            db.users.create_user(res['username'], res['passw'], res['name'], res['email'])
        except errors.EntryExists:
            res['errors'] = ["user with same name exists. try something else."]
            return res
        except errors.SomethingWentWrong as e:
            print("[!] ERROR:", e)
            res['errors'] = ["something went wrong. please try again."]
            return res
        else:
            try:
                request.cookies['user'] = db.sessions.start_session(res['username'])
            except errors.SomethingWentWrong as e:
                print("[!] ERROR:", e)
                res['errors'] = ["your signup succeeded, but there was an error later on. please, try reloging."]
                return res
            else:
                return HTTPFound(location='/hello')
    else:
        return res


@view_config(route_name='login', renderer='templates/login.pt', request_method='GET')
def login_get(request):
    return {
        'errors': [],
        'username': ''
    }


@view_config(route_name='login', renderer='templates/login.pt', request_method='POST')
def login_post(request):
    res = {
        'username': request.params['username']
    }
    try:
        db.users.validate_user(request.params['username'], request.params['passw'])
    except errors.EntryNotFound:
        res['errors'] = ["user not found. please, make sure the username is correct."]
        return res
    except errors.WrongCredentials:
        res['errors'] = ["wrong credentials. make sure your password is correct."]
        return res
    except errors.SomethingWentWrong as e:
        print("[!] ERROR:", e)
        res['errors'] = ["something went wrong. please try again."]
        return res
    else:
        try:
            request.cookies['user'] = db.sessions.start_session(res['username'])
            return HTTPFound(location='/hello')
        except errors.SomethingWentWrong as e:
            print("[!] ERROR:", e)
            res['errors'] = ["something went wrong. please try again."]
            return res


@view_config(route_name='logout')
def logout_view(request):
    try:
        db.sessions.end_session(request.cookies['user'])
        return HTTPFound(location='/hello')
    except errors.SomethingWentWrong as e:
        print("[!] ERROR:", e)
        return HTTPFound(location='/logout')
    else:
        return HTTPFound(location='/login')