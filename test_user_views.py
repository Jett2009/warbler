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

from app import app

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