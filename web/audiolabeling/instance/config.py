import os
basedir = os.path.abspath(os.path.dirname(__file__))

db_ip = os.environ.get("ANNOTATOR_DB_PORT_5432_TCP_ADDR") # ip of the linked postgres container (<linked container name>_PORT_<num port>_<protocol>_ADDR)
db_port = os.environ.get("ANNOTATOR_DB_PORT_5432_TCP_PORT") # port of the linked postgres container (<linked container name>_PORT_<num port>_<protocol>_ADDR)

DEBUG = True
WTF_CSRF_ENABLED = True
SECRET_KEY = 'this-really-needs-to-be-changed'
SQLALCHEMY_DATABASE_URI = "postgresql://myuser:mypassword@{0}:{1}/annotator_db".format(db_ip, db_port)
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Bcrypt algorithm hashing rounds
BCRYPT_LOG_ROUNDS = 15

# Email settings
MAIL_SERVER='smtp.gmail.com',
MAIL_PORT=465,
MAIL_USE_SSL=True,
MAIL_USERNAME = 'xxx',
MAIL_PASSWORD = 'xxx'

# Upload directory
UPLOAD_DIR = '/upload'
