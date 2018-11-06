from app.exceptions import NoPermissionException
from app.repositories import Repository


def roles_required(role):
    def wrapper(func):
        def check_role_and_call(*args, **kwargs):
            if Repository.is_admin_role() or Repository.check_role(role):
                return func(*args, **kwargs)
            raise NoPermissionException()
        return check_role_and_call
    return wrapper
