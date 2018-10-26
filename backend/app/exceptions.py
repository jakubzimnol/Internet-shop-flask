
class MyBaseException(Exception):
    status_code = 400
    message = 'undefined exception'

    def add_message(self, msg):
        self.message = ' '.join((self.message, msg))


class IntegrityException(MyBaseException):
    message = 'Unknown integrity error in database'


class CreateTokenException(MyBaseException):
    message = 'Creating token error, try again'
