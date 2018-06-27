import sys
import os
import shutil

from flask import url_for

from dynitag import db, app
from dynitag.models import User


# Create some initial data and commit to the database
with app.app_context():

    # Insert user data
    admin = User(username='admin', email='admin@gmail.com', plaintext_password='changeme', role='admin')
    db.session.add(admin)

    # Commit
    db.session.commit()

    print('...done!')

