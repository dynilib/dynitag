import enum
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property

from audiolabeling import db, bcrypt


class User(db.Model):
    """Copied from https://gitlab.com/patkennedy79/flask_recipe_app/blob/master/web/project/models.py"""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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

    def __init__(self, email, plaintext_password, email_confirmation_sent_on=None, role='user'):
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
        return '<User {}>'.format(self.email)


class FeedbackType(enum.Enum):
    NONE = "none"
    HIDDENIMAGE = "hiddenImage"


class VisualizationType(enum.Enum):
    WAVEFORM = "waveform"
    SPECTROGRAM = "spectrogram"


class TagType(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    annotationtags = db.relationship('AnnotationTag',
                                     backref='tagtype',
                                     lazy='dynamic')

    def __repr__(self):
        return '<id {}>'.format(self.id)


class Project(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    feedbacktype = db.Column(db.Enum(FeedbackType), nullable=False)
    visualizationtype = db.Column(db.Enum(VisualizationType), nullable=False)
    name = db.Column(db.String, unique=True, nullable=False)
    annotationtags = db.relationship('AnnotationTag',
                                     backref='projects',
                                     lazy='dynamic')
    audios = db.relationship('Audio',
                                     backref='projects',
                                     lazy='dynamic')
    #result_all = db.Column(JSON)
    #result_no_stop_words = db.Column(JSON)

    def __repr__(self):
        return '<id {}>'.format(self.id)


class AnnotationTag(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    tagtype_id = db.Column(db.Integer, db.ForeignKey(TagType.id), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey(Project.id), nullable=False)
    name = db.Column(db.String, unique=True, nullable=False)
    annotations = db.relationship('Annotation',
                                  backref='annotationtag',
                                  lazy='dynamic')

    def __repr__(self):
        return '<id {}>'.format(self.id)


class Audio(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, unique=True, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey(Project.id), nullable=False)
    annotations = db.relationship('Annotation',
                                  backref='audio',
                                  lazy='dynamic')

    def __repr__(self):
        return '<id {}>'.format(self.id)


class Annotation(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    annotationtag_id = db.Column(db.Integer, db.ForeignKey(AnnotationTag.id), nullable=False)
    audio_id = db.Column(db.Integer, db.ForeignKey('audio.id'), nullable=False)
    user_id  = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<id {}>'.format(self.id)


