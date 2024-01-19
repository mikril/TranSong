import readcompilation
from flask_login import UserMixin

class UserLogin(UserMixin):
    def fromDB(self, user_id):
        self.__user = readcompilation.getUser(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user[0])

    def get_name(self):
        return str(self.__user[1])

    def get_email(self):
        return str(self.__user[2])