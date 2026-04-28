# src/user_service/domain/exception/user_exceptions.py
class UserNotFoundError(Exception):
    pass


class DuplicateEmailError(Exception):
    pass
