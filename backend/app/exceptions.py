class ApiBaseException(Exception):
    message = None
    status_code = 400

    def __init_subclass__(cls, **kwargs):
        assert cls.message

    def to_dict(self):
        return dict(self.message)


class IntegrityException(ApiBaseException):
    message = 'Unknown integrity error in database'
