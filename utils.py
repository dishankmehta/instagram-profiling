import os


def save_cookies(session):
    try:
        if not os.path.isdir(os.path.dirname(session.cookies.filename)):
            os.mkdir(os.path.dirname(session.cookies.filename))
        session.cookies.save()
    except IOError:
        pass
