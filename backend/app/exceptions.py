class ApiBaseException(Exception):
    message = None
    status_code = 400

    def __init__(self, message=None):
        if message:
            self.message = message

    def __init_subclass__(cls, **kwargs):
        assert cls.message

    def to_dict(self):
        return {'message': self.message}


class IntegrityException(ApiBaseException):
    message = 'Unknown integrity error in database'


class PayuException(ApiBaseException):
    message = 'Error with Payu server'


class BadContentInResponse(ApiBaseException):
    message = 'Bad content in response'
