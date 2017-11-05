import os
import enum
from datetime import datetime
from flask import redirect, request, url_for
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.event import listens_for
from flask_login import current_user

from audiolabeling import app, db, bcrypt, login_manager


class User(db.Model):
    """Copied from https://gitlab.com/patkennedy79/flask_recipe_app/blob/master/web/project/models.py"""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    _password = db.Column(db.Binary(60), nullable=False)
    authenticated = db.Column(db.Boolean, default=False)
    email_confirmation_sent_on = db.Column(db.DateTime, nullable=True)
    email_confirmed = db.Column(db.Boolean, nullable=True, default=False)
    email_confirmed_on = db.Column(db.DateTime, nullable=True)
    registered_on = db.Column(db.DateTime, nullable=True)
    last_logged_in = db.Column(db.DateTime, nullable=True)
    current_logged_in = db.Column(db.DateTime, nullable=True)
    role = db.Column(db.String, default='user')
    annotations = db.relationship('Annotation', backref='user', lazy='dynamic')

    def __init__(self, username, email, plaintext_password, email_confirmation_sent_on=None, role='user'):
        self.username = username
        self.email = email
        self.password = plaintext_password
        self.authenticated = False
        self.email_confirmation_sent_on = email_confirmation_sent_on
        self.email_confirmed = False
        self.email_confirmed_on = None
        self.registered_on = datetime.now()
        self.last_logged_in = None
        self.current_logged_in = datetime.now()
        self.role = role

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def set_password(self, plaintext_password):
        self._password = bcrypt.generate_password_hash(plaintext_password)

    @hybrid_method
    def is_correct_password(self, plaintext_password):
        return bcrypt.check_password_hash(self.password, plaintext_password)

    @property
    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    @property
    def is_active(self):
        """Always True, as all users are active."""
        return True

    @property
    def is_anonymous(self):
        """Always False, as anonymous users aren't supported."""
        return False

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        """Requires use of Python 3"""
        return str(self.id)

    def generate_auth_token(self, expires_in=3600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expires_in)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User {}>'.format(self.username)


@enum.unique
class FeedbackType(enum.Enum):
    NONE = 1
    HIDDENIMAGE = 2


@enum.unique
class VisualizationType(enum.Enum):
    WAVEFORM = 1
    SPECTROGRAM = 2


class TagType(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    annotationtags = db.relationship('AnnotationTag',
                                     backref='tagtype',
                                     lazy='dynamic')

    def __repr__(self):
        return '<name {}>'.format(self.name)


audio_project_rel = db.Table('audio_project_rel',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('audio_id', db.Integer, db.ForeignKey('audio.id'), primary_key=True)
)


annotationtag_project_rel = db.Table('annotationtag_project_rel',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('annotationtag_id', db.Integer, db.ForeignKey('annotation_tag.id'), primary_key=True)
)


class Project(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    audio_root_url = db.Column(db.String, nullable=False)
    feedbacktype = db.Column(db.Enum(FeedbackType), default=FeedbackType.NONE, nullable=False)
    visualizationtype = db.Column(db.Enum(VisualizationType), default=VisualizationType.SPECTROGRAM, nullable=False)
    allowRegions = db.Column(db.Boolean, nullable=False)
    n_annotations_per_file = db.Column(db.Integer, nullable=True)
    annotationtags = db.relationship('AnnotationTag',
                                     secondary=annotationtag_project_rel,
                                     lazy='dynamic',
                                     backref=db.backref('projects', lazy=True))
    audios = db.relationship('Audio',
                             secondary=audio_project_rel,
                             lazy='dynamic',
                             backref=db.backref('projects', lazy=True))
    annotations = db.relationship('Annotation',
                                  backref='project',
                                  lazy='dynamic',
                                  cascade='all')
    audios_filename = db.Column(db.String, nullable=True)
    annotations_filename = db.Column(db.String, nullable=True)

    @property
    def is_completed(self):
        if (self.n_annotations_per_file and
                self.annotations.count() >= self.audios.count() * self.n_annotations_per_file):
            return True
        return False

    def __repr__(self):
        return '<name {}>'.format(self.name)



@listens_for(Project, 'after_delete')
def del_file(mapper, connection, target):
    if target.audios_filename:
        try:
            os.remove(os.path.join(app.config['UPLOAD_DIR'], 'audios', target.audios_filename))
        except OSError:
            # Don't care if was not deleted because it does not exist
            pass
    if target.annotations_filename:
        try:
            os.remove(os.path.join(app.config['UPLOAD_DIR'], 'annotations', target.annotations_filename))
        except OSError:
            # Don't care if was not deleted because it does not exist
            pass


class AnnotationTag(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    tagtype_id = db.Column(db.Integer, db.ForeignKey(TagType.id), nullable=False)
    name = db.Column(db.String, unique=True, nullable=False)
    annotations = db.relationship('Annotation',
                                  backref='annotationtag',
                                  lazy='dynamic',
                                  cascade='all')

    def __repr__(self):
        return '<name {}>'.format(self.name)


class Audio(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    rel_path = db.Column(db.String, unique=True, nullable=False)
    annotations = db.relationship('Annotation',
                                  backref='audio',
                                  lazy='dynamic',
                                  cascade='all')

    def __repr__(self):
        return '<id {}>'.format(self.id)


class Annotation(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.Float, nullable=True)
    end_time = db.Column(db.Float, nullable=True)
    annotationtag_id = db.Column(db.Integer, db.ForeignKey(AnnotationTag.id), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    audio_id = db.Column(db.Integer, db.ForeignKey('audio.id'), nullable=False)
    user_id  = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<id {}>'.format(self.id)

