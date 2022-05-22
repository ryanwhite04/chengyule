from test import Case, db
from app.models import (
    User,
    Game,
    Play,
    Note,
    Text,
    Code,
)

class ModelCase(Case):

    def show(self):
        plays = Play.query.all()
        users = User.query.all()
        games = Game.query.all()
        print(f"{plays=}, {users=}, {games=}")

class StatsModelCase(ModelCase):

    def test(self):
        a = User(username="a", email="a@a.a", password="a")
        b = User(username="b", email="b@b.b", password="b")
        c = Game(word="d")
        d = Game(word="d")
        a.play(c, 'a')
        a.play(d, 'a')
        a.play(d, 'd') # Correct
        b.play(c, 'a')
        db.session.add_all([a])
        db.session.commit()
        self.assertEqual(len(a.games), 2) # A played 2 games
        self.assertEqual(len(b.games), 1) # B played 1 game
        self.assertEqual(a.attempts, 3) # A played 3 moves
        self.assertEqual(b.attempts, 1) # B played 1 move

class NoteModelCase(ModelCase):

    def show(self):
        texts = Text.query.all()
        codes = Code.query.all()
        notes = Note.query.all()
        print(f"{texts=}\n{codes=}\n{notes=}")

    def test_create(self):
        西班牙语 = Text("西班牙语") # Spanish
        英语 = Text("英语") # English
        你好 = Text("你好") # Hello
        es = Code("es", "西班牙语")
        en = Code("en", "英语")
        hello = Note("Hello", "en", "你好")
        hola = Note("Hola", "es", "你好")
        db.session.add_all([西班牙语, 英语, 你好])
        db.session.add_all([es, en])
        db.session.add_all([hello, hola])
        db.session.commit()
        self.assertEqual(
            "[<Text 西班牙语>, <Text 英语>, <Text 你好>]",
            str(Text.query.all()))
        self.assertEqual(
            "[<Code es is 西班牙语>, <Code en is 英语>]",
            str(Code.query.all()))
        self.assertEqual(
            "[<Note Hello is en for 你好>, <Note Hola is es for 你好>]",
            str(Note.query.all()))

class PlayModelCase(ModelCase):

    def test_secondPlay(self):
        u = User(username="a", email="a@a.a", password="a")
        g = Game(word="a")
        p = u.play(g, "b")
        u.play(g, "c") # this changes the first p
        self.assertCountEqual(Play.query.all(), (p,))
        self.assertCountEqual(User.query.all(), (u,))
        self.assertCountEqual(Game.query.all(), (g,))

    def test_commitNotCalled(self):
        u = User(username="a", email="a@a.a", password="a")
        db.session.add(u)
        db.session.flush()
        g = Game(word="a")
        u.play(g, "a")
    
    def test_wrongWordLength(self):
        u = User(username="a", email="a@a.a", password="a")
        db.session.add(u)
        db.session.commit()
        g = Game(word="a")
        with self.assertRaises(ValueError) as context:
            u.play(g, "aa")
        self.assertTrue("Can't play that word" in str(context.exception))
        db.session.rollback()
        self.assertCountEqual(User.query.all(), (u,))
        self.assertFalse(Play.query.all()) # Play wasn't commited
        self.assertFalse(Game.query.all()) # Game wasn't commited
    
    def populate(self):
        users = (
            User(username="a", email="a@a.a", password="a"),
            User(username="b", email="b@b.b", password="b"),
            User(username="c", email="c@c.c", password="c"),
        )
        games = (
            Game(word="x"),
            Game(word="y"),
            Game(word="z"),
        )

        for i, user in enumerate(users):
            user.play(games[i], ["a", "b", "c"][i])
            user.play(games[i], ["d", "e", "f"][i])
            user.play(games[(i+1)%len(games)], ["a", "b", "c"][i])

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

class UserModelCase(ModelCase):

    def test_password_hashing(self):
        from werkzeug.security import generate_password_hash
        password = generate_password_hash("a")
        u = User(username="a", email="a@a.a", password=password)
        self.assertTrue(u.checkPassword("a"))
        self.assertFalse(u.checkPassword("b"))
