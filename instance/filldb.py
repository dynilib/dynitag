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

    admin = User(email='jujul@gmail.com', plaintext_password='password1234', role='admin')
    db.session.add(admin)
    user1 = User(email='jujulj@gmail.com', plaintext_password='password1234', role='user')
    db.session.add(user1)

    # Insert other data

    tagtype1 = TagType()
    tagtype1.name = "species"
    db.session.add(tagtype1)
    
    db.session.commit()
    
    anntag1 = AnnotationTag()
    anntag1.name = "Bird1"
    anntag1.tagtype_id = tagtype1.id
    
    anntag2 = AnnotationTag()
    anntag2.name = "Bird2"
    anntag2.tagtype_id = tagtype1.id
    
    tagtype2 = TagType()
    tagtype2.name = "proximity"
    db.session.add(tagtype2)
    
    db.session.commit()
    
    anntag3 = AnnotationTag()
    anntag3.name = "Close"
    anntag3.tagtype_id = tagtype2.id
    
    anntag4 = AnnotationTag()
    anntag4.name = "Medium"
    anntag4.tagtype_id = tagtype2.id
    
    anntag5 = AnnotationTag()
    anntag5.name = "Far"
    anntag5.tagtype_id = tagtype2.id
    
    audio1 = Audio()
    audio1.url = "audio/ID1278.wav"

    audio2 = Audio()
    audio2.url = "audio/ID1283.wav"

    audio3 = Audio()
    audio3.url = "audio/ID1284.wav"

    project1 = Project()
    project1.feedbacktype = FeedbackType.NONE
    project1.visualizationtype = VisualizationType.SPECTROGRAM
    project1.name = "project1"
    project1.allowRegions = False
    project1.annotationtags.append(anntag1)
    project1.annotationtags.append(anntag2)
    project1.annotationtags.append(anntag3)
    project1.annotationtags.append(anntag4)
    project1.annotationtags.append(anntag5)
    project1.audios.append(audio1)
    project1.audios.append(audio2)
    project1.audios.append(audio3)
    db.session.add(project1)

    # Commit
    db.session.commit()

    print('...done!')

