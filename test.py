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
    
    def test_multiplePlays(self):
        u = User(username="a", email="a@a.a", password="a")
        g = Game(word="a")
        db.session.add(u)
        db.session.add(g)
        db.session.add(u.play(g, "a"))
        db.session.add(u.play(g, "b"))
        db.session.commit()
        plays = Play.query.all()
        print(f"{plays=}")

    def test_wrongWordLength(self):
        u = User(username="a", email="a@a.a", password="a")
        g = Game(word="a")
        with self.assertRaises(ValueError) as context:
            u.play(g, "aa")
        self.assertTrue("Can't play that word" in str(context.exception))

    def populate(self):
        users = (
            User(username="a", email="a@a.a", password="a"),
            User(username="b", email="b@b.b", password="b"),
            User(username="c", email="c@c.c", password="c"),
        )
        games = (
            Game(word="a"),
            Game(word="b"),
            Game(word="c"),
        )

        db.session.add_all(games)
        db.session.add_all(users)
        for i, user in enumerate(users):
            db.session.add(user.play(games[i], ["a", "b", "c"][i]))
            db.session.add(user.play(games[(i+1)%len(games)], ["a", "b", "c"][i]))

        db.session.commit()
        return games, users

    def test_playGame(self):

        games, users = self.populate()

        for i, user in enumerate(User.query.all()):
            self.assertCountEqual(
                user.games,
                (games[i], games[(i+1) % len(games)])
            )
        for i, game in enumerate(Game.query.all()):
            self.assertCountEqual(
                game.users,
                (users[(i+2) % len(users)], users[i])
            )

if __name__ == "__main__": main()
