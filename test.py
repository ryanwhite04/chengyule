from app import create_app, db
from config import Config
from unittest import TestCase, main
from app.models import User, Game, Play

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"

class UserModelCase(TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        from werkzeug.security import generate_password_hash
        password = generate_password_hash("a")
        u = User(username="a", email="a@a.a", password=password)
        self.assertTrue(u.checkPassword("a"))
        self.assertFalse(u.checkPassword("b"))

if __name__ == "__main__": main()
