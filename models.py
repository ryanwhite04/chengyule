from app import db

# From https://flask-user.readthedocs.io/en/latest/data_models.html
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # User Authentication fields
    email = db.Column(db.String(255), nullable=False, unique=True)
    email_confirmed_at = db.Column(db.DateTime())
    username = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    plays = db.relationship("Play", backref="user", lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(255), nullable=False)
    plays = db.relationship("Play", backref="game", lazy=True)

    def __repr__(self):
        return f'<Game {self.word}>'

class Play(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey("user.id"))
    game = db.Column(db.Integer, db.ForeignKey("game.id"))
    time = db.Column(db.DateTime(), index=True)
    word = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Play {self.word} at {self.time}>'

