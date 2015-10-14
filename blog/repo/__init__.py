__author__ = 'tyerq'


def schema():
    return """
posts:
    permalink == _id
    author == nickname
    posted
    topic
    text
    comments == [
        comment:
            author == nickname
            posted
            text
        ...
        ]
    tags == [
        tag
        ...
        ]

users:
    username == _id
    passw
    name
    email

sessions:
    token == _id
    user
    """