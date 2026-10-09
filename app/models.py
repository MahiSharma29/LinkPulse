from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db, login_manager


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    links = db.relationship("Link", backref="owner", lazy="dynamic", cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    code = db.Column(db.String(32), unique=True, nullable=False, index=True)
    target_url = db.Column(db.String(2048), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    clicks = db.relationship("Click", backref="link", lazy="dynamic", cascade="all, delete-orphan")


class Click(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.Integer, db.ForeignKey("link.id"), nullable=False, index=True)
    clicked_at = db.Column(db.DateTime, default=utcnow, nullable=False, index=True)
    referrer = db.Column(db.String(255))
    user_agent = db.Column(db.String(255))


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))
