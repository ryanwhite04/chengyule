from flask_login import UserMixin
from werkzeug.security import check_password_hash
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates

# From https://flask-user.readthedocs.io/en/latest/data_models.html

from app import db, login

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)

    # User Authentication fields
    email = db.Column(db.String(255), nullable=False, unique=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    games = association_proxy("plays", "game")
    def play(self, game, word):
        p = Play(word=word)
        self.plays.append(p)
        game.plays.append(p)
        return p

    def checkPassword(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.username}>'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Game(db.Model):
    __tablename__ = "games"
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(255), nullable=False)
    users = association_proxy("plays", "user")
    @validates("plays")
    def check(self, key, play):
        if len(self.word) != len(play.word):
            raise ValueError("Can't play that word", self.word, play.word)
        return play
    def __repr__(self):
        return f'<Game {self.word}>'

class Play(db.Model):
    __tablename__ = "plays"
    user_id = db.Column(db.ForeignKey("users.id"), primary_key=True)
    game_id = db.Column(db.ForeignKey("games.id"), primary_key=True)
    word = db.Column(db.String(255), nullable=False, primary_key=True)
    user = db.relationship("User", backref="plays")
    game = db.relationship("Game", backref="plays")

    def __repr__(self):
        return f'<Play word={self.word} user={self.user.username} game={self.game.word}>'
