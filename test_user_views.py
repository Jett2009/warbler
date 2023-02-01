import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()
# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

class UserModelTestCase(TestCase):
    """Test views for messages."""
    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        # Sample Data Below

        # User table
        u1 = User.signup("test1", "test1@test.com", "password", None)
        u1_id = 123
        u1.id = u1_id

        u2 = User.signup("test2", "test2@test.com", "password", None)
        u2_id = 456
        u2.id = u2_id

        u3 = User.signup("test3", "test3@test.com", "password", None)
        u3_id = 456
        u3.id = u3_id

        db.session.commit()

        u1 = User.query.get(u1_id)
        u2 = User.query.get(u2_id)
        u3 = User.query.get(u3_id)

        self.u1 = u1
        self.u1_id = u1_id

        self.u2 = u2
        self.u2_id = u2_id

        self.u3 = u3
        self.u3_id = u3_id

        # End of Sample Data

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_users_index(self):
        """Test route '/users'"""

        with self.client as c:
            resp = c.get('/users')

            self.assertIn("@test1", str(resp.data))
            self.assertIn("@test2", str(resp.data))
            self.assertIn("@test3", str(resp.data))

    def test_users_show(self):
        """Test route '/users/<user_id>'"""

        with self.client as c:
            resp = c.get(f'/users/{self.u1_id}')

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@test1", str(resp.data))

    def test_users_show_following(self):
        """Test route '/users/<user_id>/following"""

        # test2 is following test1
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            user2 = User.query.get(self.u2_id)

            resp = c.get(f'/users/{user2.id}/following')

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@test1", str(resp.data))

            # Make u2 follow u3, refresh following page and check u3 is included
            user2.following.append(self.u3)
            db.session.commit()

            resp = c.get(f'/users/{user2.id}/following')
            self.assertIn("@test3", str(resp.data))

    def test_users_add_remove_follow(self):
        """Test that POST route '/users/follow/<follow_id>' works correctly"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u3_id

            # First check test1 is not being followed by test3
            resp = c.get(f'/users/{self.u3_id}/following')
            self.assertNotIn("@test1", str(resp.data))
            
            # Have u3 follow u1
            resp = c.post(f'/users/follow/{self.u1_id}',
                            follow_redirects=True)

         

    def test_users_show_followers(self):
        """Test route '/users/<user_id>/followers"""

        # test1 has a follower test2
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            user1 = User.query.get(self.u1_id)

            resp = c.get(f'/users/{user1.id}/followers')

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@test2", str(resp.data))

            # make u3 follow u1,

            user1.followers.append(self.u3)
            db.session.commit()

            resp = c.get(f'/users/{user1.id}/followers')

            self.assertIn("@test3", str(resp.data))

    def test_users_likes(self):
        """Test route '/users/<user_id>/likes' page"""

        # test1 has one liked message
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            
            user1 = User.query.get(self.u1_id)
            msg2 = Message.query.filter(Message.user_id == self.u2_id).first()

            resp = c.get(f'/users/{user1.id}/likes')

            self.assertEqual(resp.status_code, 200)
            self.assertIn(msg2.text, str(resp.data))

            # Add test3 message to test1 likes, refresh page and check m3 is included
            user1.likes.append(self.m3)
            db.session.commit()

            m3 = Message.query.filter(Message.user_id == self.u3_id).first()

            resp = c.get(f'/users/{user1.id}/likes')

            self.assertIn(m3.text, str(resp.data))

    def test_users_profile(self):
        """Test route '/users/profile' POST route"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            
            #Logged in as test1
            resp = c.get('/users/profile')

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test1", str(resp.data))


            # Change test1 username to 1test and check for change
            user1 = User.query.get(self.u1_id)

            resp = c.post('/users/profile',
                        data={'username': '1test', 'email': user1.email, 'image_url': user1.image_url, 'header_image_url': user1.header_image_url, 'bio': user1.bio},
                        follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("1test", str(resp.data))

    def test_users_delete(self):
        """Test route '/users/delete' POST route"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            #Logged in as test1. Delete self

            resp = c.post('/users/delete', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Join Warbler today.", str(resp.data))

    