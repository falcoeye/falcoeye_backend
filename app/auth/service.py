from datetime import datetime

from flask import current_app
from flask_jwt_extended import create_access_token

from app import db
from app.dbmodels.schemas import UserSchema
from app.dbmodels.user import User as User
from app.utils import err_resp, internal_err_resp, message

user_schema = UserSchema()


class AuthService:
    @staticmethod
    def login(data):
        # Assign vars
        email = data.get("email", None)
        password = data.get("password", None)
        if email is None or password is None:
            return err_resp(
                "invalid data",
                "invalid_403",
                403,
            )
        try:
            # Fetch user data
            if "@" in email:
                if not (user := User.query.filter_by(email=email).first()):
                    return err_resp(
                        "usern not found",
                        "user_404",
                        404,
                    )
            else:
                if not (user := User.query.filter_by(username=email).first()):
                    return err_resp(
                        "usern not found",
                        "user_404",
                        404,
                    )

            if user.verify_password(password):
                user_info = user_schema.dump(user)

                access_token = create_access_token(
                    identity=user.id,
                    expires_delta=current_app.config["JWT_ACCESS_TOKEN_EXPIRES"],
                )

                resp = message(True, "successfully logged in")
                resp["access_token"] = access_token
                resp["user"] = user_info

                return resp, 200

            return err_resp("incorrect username or password", "password_invalid", 401)

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()

    @staticmethod
    def register(data):
        # Assign vars

        ## Required values
        email = data["email"]
        username = data["username"]
        password = data["password"]

        ## Optional
        data_name = data.get("name")

        # Check if the email is taken
        if User.query.filter_by(email=email).first() is not None:
            return err_resp("email or username already exists", "email_taken", 403)

        # Check if the username is taken
        if User.query.filter_by(username=username).first() is not None:
            return err_resp(
                "username or username already exists", "username_taken", 403
            )

        try:
            new_user = User(
                email=email,
                username=username,
                name=data_name,
                password=password,
                joined_date=datetime.utcnow(),
            )

            db.session.add(new_user)
            db.session.flush()

            # Load the new user's info
            user_info = user_schema.dump(new_user)

            # Commit changes to DB
            db.session.commit()

            # Create an access token
            access_token = create_access_token(
                identity=new_user.id,
                expires_delta=current_app.config["JWT_ACCESS_TOKEN_EXPIRES"],
            )

            resp = message(True, "successfully registered")
            resp["access_token"] = access_token
            resp["user"] = user_info

            return resp, 201

        except Exception as error:
            current_app.logger.error(error)
            return internal_err_resp()
