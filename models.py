from app import db

# From https://flask-user.readthedocs.io/en/latest/data_models.html
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    # User Authentication fields
    email = db.Column(db.String(255), nullable=False, unique=True)
    email_confirmed_at = db.Column(db.DateTime())
    username = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Play(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)

    # User Authentication fields
    user = db.Column(db.Integer, nullable=False)
    time = db.Column(db.DateTime(), nullable=False)
    word = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Play {self.word} at {self.time}>'