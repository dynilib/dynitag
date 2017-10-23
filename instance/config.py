import os
basedir = os.path.abspath(os.path.dirname(__file__))


DEBUG = True
WTF_CSRF_ENABLED = True
SECRET_KEY = 'this-really-needs-to-be-changed'
SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

# Bcrypt algorithm hashing rounds
BCRYPT_LOG_ROUNDS = 15

# Email settings
MAIL_SERVER='smtp.gmail.com',
MAIL_PORT=465,
MAIL_USE_SSL=True,
MAIL_USERNAME = 'audiolabeling@gmail.com',
MAIL_PASSWORD = 'audi4Basta'

# Upload directory
UPLOAD_DIR = '/home/jul/dev/audiolabeling/upload/'

