from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Post

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username='susan',user_level = 3)
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128'))

    def test_join(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u1.set_password('cat')
        u2.set_password('dog')
        p = post = Post(title="test", body = "test body",
                    user_id = u2,max_participant=20)
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(p)
        db.session.commit()
        # self.assertEqual(u1.followed.all(), [])
        # self.assertEqual(u1.followers.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        # self.assertEqual(u1.followed.count(), 1)
        # self.assertEqual(u1.followed.first().username, 'susan')
        # self.assertEqual(u2.followers.count(), 1)
        # self.assertEqual(u2.followers.first().username, 'john')


