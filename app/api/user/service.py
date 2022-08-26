from flask import current_app

from app import db
from app.dbmodels.user import User as User
from app.utils import err_resp, internal_err_resp, message

from .utils import load_data


class UserService:
    @staticmethod
    def get_user_data(userid):
        """Get user data by username"""
        if not (user := User.query.filter_by(id=userid).first()):
            return err_resp("user not found", "user_404", 404)

        try:
            user_data = load_data(user)

            resp = message(True, "user data sent")
            resp["user"] = user_data
            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def delete_user(userid):
        """Delete user from DB by username"""
        if not (user := User.query.filter_by(id=userid).first()):
            return err_resp("user not found", "user_404", 404)

        try:
            db.session.delete(user)
            db.session.commit()

            resp = message(True, "user deleted")
            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def edit_user(userid, data):
        """Edit user from DB by id"""
        if not (user := User.query.filter_by(id=userid).first()):
            return err_resp("user not found", "user_404", 404)

        name = data.get("name", user.name)
        email = data.get("email", user.email)
        username = data.get("username", user.email)
        if username != user.username:
            if User.query.filter_by(username=username).first() is not None:
                return err_resp("username or email exists", "user_taken", 403)
        if email != user.email:
            if User.query.filter_by(email=email).first() is not None:
                return err_resp("username or email exists", "email_taken", 403)

        try:
            user.name = name
            user.email = email
            user.username = username

            db.session.flush()
            db.session.commit()

            user_data = load_data(user)
            resp = message(True, "user data sent")
            resp["user"] = user_data
            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()
