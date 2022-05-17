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
        """
        If user has already played this game
            return existing play
        else create new play
        set play word
        """
        # this ensures game/user have ids for the following query
        db.session.add(game)
        db.session.add(self)
        db.session.flush()
        p = Play.query.get({
            "user_id": self.id,
            "game_id": game.id,
        }) or Play(game=game, user=self)
        try:
            # will fail if word doesn't obey rules
            # This is checked in the validator for word in Play
            p.word = word
            return p
        except:
            raise

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
    attempts = db.Column(db.Integer, nullable=False)

    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)
        self.attempts = 4
    
    def __repr__(self):
        return f'<Game {self.word}>'

class Play(db.Model):
    __tablename__ = "plays"
    user_id = db.Column(db.ForeignKey("users.id"), primary_key=True)
    game_id = db.Column(db.ForeignKey("games.id"), primary_key=True)
    word = db.Column(db.String(255), nullable=False)
    user = db.relationship("User", backref="plays")
    game = db.relationship("Game", backref="plays")
    attempt = db.Column(db.Integer, nullable=False)
    correct = db.Column(db.Boolean, nullable=False)

    def __init__(self, **kwargs):
        super(Play, self).__init__(**kwargs)
        self.attempt = 0
        self.correct = False

    @validates("word")
    def check(self, key, word):
        if len(self.game.word) != len(word):
            raise ValueError("Can't play that word", word, self.game.word)
        if self.game.attempts == self.attempt:
            raise Exception("Maximum attempts reached", self.game.attempts, self.attempt)
        if self.correct:
            raise Exception("This game is already complete")
        if self.game.word == word:
            self.correct = True
        self.attempt += 1
        return word

    def __repr__(self):
        return f'<Play word={self.word} user={self.user.username} game={self.game.word}>'

class Text(db.Model):
    __tablename__ = "texts"
    id = db.Column(db.String, primary_key=True)

    def __init__(self, text: str):
        self.id = text

    def __repr__(self):
        return f'<Text {self.id}>'

class Code(db.Model):
    __tablename__ = "codes"
    id = db.Column(db.String, primary_key=True)
    text = db.Column(db.ForeignKey("texts.id"))

    def __init__(self, code: str, text: str):
        self.id = code
        self.text = text

    def __repr__(self):
        return f'<Code {self.id} is {self.text}>'

class Note(db.Model):
    __tablename__ = "notes"
    text = db.Column(db.ForeignKey("texts.id"), primary_key=True)
    code = db.Column(db.ForeignKey("codes.id"), primary_key=True)
    content = db.Column(db.String, nullable=False)

    def __init__(self, note: str, code: str, text: str):
        self.text = text
        self.code = code
        self.content = note

    def __repr__(self):
        return f'<Note {self.content} is {self.code} for {self.text}>'

