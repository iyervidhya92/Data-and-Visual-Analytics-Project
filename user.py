

class User(object):
    """An admin user capable of viewing reports.

    :param str email: email address of user
    :param str password: encrypted password for the user

    """
    def __init__(self,user_id):
        self.email = user_id
        self.authenticated = False

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return self.authenticated

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.email

    def set_authenticated(self):
        self.authenticated = True