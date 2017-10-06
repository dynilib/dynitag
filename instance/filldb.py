import sys
import os
import shutil

from flask import url_for

from audiolabeling import db, app
from audiolabeling.models import (User, TagType, AnnotationTag, Audio,
                                  Project, FeedbackType, VisualizationType)


# Create some initial data and commit to the database
with app.app_context():

    # Insert user data
    user1 = User(email='jujulj@gmail.com', plaintext_password='password1234', role='user')
    db.session.add(user1)

    # Insert other data
    tagtype1 = TagType()
    tagtype1.name = "species"
    db.session.add(tagtype1)

    project1 = Project()
    project1.feedbacktype = FeedbackType.NONE
    project1.visualizationtype = VisualizationType.SPECTROGRAM
    project1.name = "project1"
    db.session.add(project1)
    
    db.session.commit()

    anntag1 = AnnotationTag()
    anntag1.name = "Bird1"
    anntag1.tagtype_id = tagtype1.id
    anntag1.project_id = project1.id
    db.session.add(anntag1)

    anntag2 = AnnotationTag()
    anntag2.name = "Bird2"
    anntag2.tagtype_id = tagtype1.id
    anntag2.project_id = project1.id
    db.session.add(anntag2)
    
    audio1 = Audio()
    audio1.url = "audio/ID1278.wav"
    audio1.project_id = project1.id
    db.session.add(audio1)

    audio2 = Audio()
    audio2.url = "audio/ID1283.wav"
    audio2.project_id = project1.id
    db.session.add(audio2)

    audio3 = Audio()
    audio3.url = "audio/ID1284.wav"
    audio3.project_id = project1.id
    db.session.add(audio3)

    # Commit the changes for the recipes
    db.session.commit()

    print('...done!')

