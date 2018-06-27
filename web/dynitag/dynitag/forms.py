from flask_wtf import FlaskForm
from wtforms import SelectField


from audiolabeling.models import Project


class ProjectForm(FlaskForm):

    project = SelectField(u'Project', coerce=int)

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.project.choices = [(p.id, p.name) for p in Project.query.order_by(Project.name)]
