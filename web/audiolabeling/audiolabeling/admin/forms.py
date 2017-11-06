from flask_wtf import FlaskForm
from wtforms import SelectField

from audiolabeling.models import Project


class GetAnnotationsForm(FlaskForm):

    project = SelectField(u'Project', coerce=int)

    def __init__(self, *args, **kwargs):
        super(GetAnnotationsForm, self).__init__(*args, **kwargs)
        self.project.choices = [(p.id, "{}{}".format(p.name, " (completed)" if p.is_completed else "")) for p in Project.query.all()]
