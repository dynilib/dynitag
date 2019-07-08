from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bcrypt import Bcrypt


app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "users.login"

from dynitag import views
from dynitag import models

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.filter(models.User.id == int(user_id)).first()

##############
# blueprints #
##############

from dynitag.users.views import users_blueprint

# register the blueprints
app.register_blueprint(users_blueprint, url_prefix='/users')

###############
# flask-admin #
###############

import dynitag.admin.views as admin_views

admin = Admin(app, name='Audiolabeling', template_mode='bootstrap3', index_view=admin_views.MyHomeView(), base_template='admin/base_with_header.html')
admin.add_view(admin_views.UserAdminView(models.User, db.session))
#admin.add_view(admin_views.AdminModelView(models.TagType, db.session))
#admin.add_view(admin_views.AdminModelView(models.AnnotationTag, db.session))
admin.add_view(admin_views.ProjectAdminView(models.Project, db.session))
