import uuid
from datetime import datetime

from flask import current_app

from app import bcrypt, db
from app.dbmodels.base import GUID

# Alias common DB names
Column = db.Column
Model = db.Model
relationship = db.relationship


class Permission:
    ADD_WORKFLOW = 0
    DELETE_WORKFLOW = 1
    ADD_ANALYSIS = 2
    VIEW_ANALYSIS = 3
    DELETE_ANALYSIS = 4
    STOP_ANALYSIS = 5
    CHANGE_CAPTURE_STATUS = 6


N = 16
PERMISSIONS_BIN = [2**i for i in range(N)]


def permissions_to_integer(permissions):
    i = [0] * N
    for p in permissions:
        i[p] = PERMISSIONS_BIN[p]
    return sum(i)


def _has_permission(int_permissions, perm_index):
    b = bin(int_permissions).split("0b")[1]
    return int(b[perm_index]) == 1


class Role(Model):
    __tablename__ = "roles"
    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(db.String(64), unique=True)
    default = Column(db.Boolean, default=False, index=True)
    permissions = Column(db.Integer)
    description = Column(db.String(50))

    users = db.relationship("User", backref="role", lazy="dynamic")

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def __repr__(self):
        return f"<{self.name} - {self.id}>"

    @staticmethod
    def insert_roles():
        roles = {
            "User": [
                Permission.ADD_ANALYSIS,
                Permission.VIEW_ANALYSIS,
                Permission.DELETE_ANALYSIS,
            ],
            "Admin": [
                Permission.ADD_WORKFLOW,
                Permission.DELETE_WORKFLOW,
                Permission.ADD_ANALYSIS,
                Permission.VIEW_ANALYSIS,
                Permission.DELETE_ANALYSIS,
                Permission.STOP_ANALYSIS,
                Permission.CHANGE_CAPTURE_STATUS,
            ],
        }

        default_role = "User"
        for r, p in roles.items():
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r, permissions=permissions_to_integer(p))
                role.default = role.name == default_role
                db.session.add(role)

        db.session.commit()

    def has_permission(self, perm):
        return self.permissions & _has_permission(self.permissions, perm)


class User(Model):
    """User model for storing user related data"""

    __tablename__ = "user"
    id = Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(db.String(64), unique=True, index=True)
    username = Column(db.String(15), unique=True, index=True)
    name = Column(db.String(64))
    password_hash = Column(db.String(128))

    joined_date = Column(db.DateTime, default=datetime.utcnow)
    role_id = Column(GUID(), db.ForeignKey("roles.id"))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config.get("FLASK_ADMIN"):
                self.role = Role.query.filter_by(name="Admin").first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

    def has_permission(self, permission):
        role = Role.query.filter_by(id=self.role_id).first()
        return role.has_permission(permission)
