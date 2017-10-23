from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import SelectField, StringField, BooleanField, IntegerField
from wtforms.validators import DataRequired


from audiolabeling.models import FeedbackType, VisualizationType, Project


class CreateProjectForm(FlaskForm):

    name = StringField('name', validators=[DataRequired()])
    feedback_type = SelectField(u'Feedback Type', coerce=int)
    visualization_type = SelectField(u'Visualization Type', coerce=int)
    allow_regions = BooleanField(u'Allow Regions')
    n_annotations_per_file = IntegerField('Number of annotators per file', default=1, validators=[DataRequired()])
    annotation_tags = FileField(validators=[FileRequired()])
    audio_root_url = StringField('Audio root URL', validators=[DataRequired()])
    audios = FileField(validators=[FileRequired()])

    def __init__(self, *args, **kwargs):
        super(CreateProjectForm, self).__init__(*args, **kwargs)
        self.feedback_type.choices = [(f.value, f.name) for f in FeedbackType]
        self.visualization_type.choices = [(v.value, v.name) for v in VisualizationType]


class GetAnnotationsForm(FlaskForm):

    project = SelectField(u'Project', coerce=int)

    def __init__(self, *args, **kwargs):
        super(GetAnnotationsForm, self).__init__(*args, **kwargs)
        self.project.choices = [(p.id, p.name) for p in Project.query.all()]
