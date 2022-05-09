from app import db

# From https://flask-user.readthedocs.io/en/latest/data_models.html
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)

    # User Authentication fields
    email = db.Column(db.String(255), nullable=False, unique=True)
    email_confirmed_at = db.Column(db.DateTime())
    username = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    plays = db.relationship("Play", backref="users.id", lazy=True)

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