import sys
import os
import shutil

from flask import url_for

from audiolabeling import db, app
from audiolabeling.models import User


# Create some initial data and commit to the database
with app.app_context():

    # Insert user data
    admin = User(username='admin', email='admin@gmail.com', plaintext_password='changeme', role='admin')
    db.session.add(admin)

    # Commit
    db.session.commit()

    print('...done!')

