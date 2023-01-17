import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Likes


# Testing Table 
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


from app import app

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.uid = 123
        u = User.signup("test", "test@test.com", "password", None)
        u.id = self.uid
        db.session.commit()

        

        self.u = User.query.get(self.uid)

        self.client = app.test_client()

# Test DB teardown to reset table
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message(self):
        """Does basic model work?"""
        
        m = Message(
            text="a warble test",
            user_id=self.uid
        )

        db.session.add(m)
        db.session.commit()

    
        self.assertEqual(len(self.u.messages), 1)
        self.assertEqual(self.u.messages[0].text, "a warble test")

    def test_likes(self):
        m1 = Message(
            text="a warble test",
            user_id=self.uid
        )

        m2 = Message(
            text="a second warble test",
            user_id=self.uid 
        )

        u = User.signup("Test2", "test2@test.com", "password", None)
        uid = 456
        u.id = uid
        db.session.add_all([m1, m2, u])
        db.session.commit()

        u.likes.append(m1)

        db.session.commit()

        l = Likes.query.filter(Likes.user_id == uid).all()
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].message_id, m1.id)