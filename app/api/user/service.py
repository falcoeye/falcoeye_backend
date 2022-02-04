from flask import current_app

from app import db
from app.dbmodels.user import User as User
from app.utils import err_resp, internal_err_resp, message


class UserService:
    @staticmethod
    def get_user_data(username):
        """Get user data by username"""
        if not (user := User.query.filter_by(username=username).first()):
            return err_resp("User not found!", "user_404", 404)

        from .utils import load_data

        try:
            user_data = load_data(user)

            resp = message(True, "User data sent")
            resp["user"] = user_data
            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def delete_user(username):
        """Delete user from DB by username"""
        if not (user := User.query.filter_by(username=username).first()):
            return err_resp("User not found!", "user_404", 404)

        try:
            db.session.delete(user)
            db.session.commit()

            resp = message(True, "User deleted")
            return resp, 200

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()
