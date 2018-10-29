
class MyBaseException(Exception):
    def __init__(self, status_code=400, message='undefined exception'):
        self.status_code = status_code
        self.message = message

    def add_message(self, msg):
        self.message = ' '.join((self.message, msg))


class IntegrityException(MyBaseException):
    message = 'Unknown integrity error in database'


class CreateTokenException(MyBaseException):
    message = 'Creating token error, try again'
