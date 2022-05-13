from app import db, login
from flask_login import UserMixin
from werkzeug import check_password_hash

# From https://flask-user.readthedocs.io/en/latest/data_models.html

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)

    # User Authentication fields
    email = db.Column(db.String(255), nullable=False, unique=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    plays = db.relationship("Play", backref="users.id", lazy=True)
    def checkPassword(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Game(db.Model):
    __tablename__ = "games"
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, index=True)
    plays = db.relationship("Play", backref="games.id", lazy=True)

    def __repr__(self):
        return f'<Game {self.word}>'

class Play(db.Model):
    __tablename__ = "plays"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey("users.id"))
    game = db.Column(db.Integer, db.ForeignKey("games.id"))
    time = db.Column(db.Time, index=True)
    word = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Play {self.word} at {self.time}>'

db.create_all()
db.session.commit()
