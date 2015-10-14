import re

__author__ = 'tyerq'


USERNAME_RE = re.compile(r"^[a-z0-9_-]{3,32}$")
PASS_RE = re.compile(r"^.{8,128}$")
NAME_RE = re.compile(r"^[^{}:;%$*()~]{3,64}$")


def validate_signup(username, passw, repeat, name, email):
    result = {
        'ok': True,
        'errors': [],
        'username': username,
        'passw': passw,
        'name': name,
        'email': email
    }
    if not USERNAME_RE.match(username):
        result['ok'] = False
        error = "bad username. try using lowercase letters and digits, also '-' and '_', make it 3 to 32 chars long"
        result['errors'].append(error)

    if not PASS_RE.match(passw):
        result['ok'] = False
        error = "bad password. make sure it's at least 8 characters long"
        result['errors'].append(error)

    if passw != repeat:
        result['ok'] = False
        error = "passwords don't match."
        result['errors'].append(error)

    if name and not NAME_RE.match(name):
        result['ok'] = False
        error = "that doesn't look like a valid name. try not using punctuation marks, make it 3 to 64 characters long"
        result['errors'].append(error)

    return result
