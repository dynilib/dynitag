from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bcrypt import Bcrypt


app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('flask.cfg')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "users.login"

from . import views
from . import models

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.filter(models.User.id == int(user_id)).first()

####################
#### blueprints ####
####################

from audiolabeling.users.views import users_blueprint

# register the blueprints
app.register_blueprint(users_blueprint, url_prefix='/users')

