import re
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import SelectField, StringField, BooleanField, IntegerField
from wtforms.validators import DataRequired, ValidationError

from audiolabeling import db
from audiolabeling.models import FeedbackType, VisualizationType, Project


class CreateProjectForm(FlaskForm):

    name = StringField('Name', validators=[DataRequired()])
    #feedback_type = SelectField(u'Feedback Type', coerce=int)
    visualization_type = SelectField(u'Visualization Type', coerce=int, default=VisualizationType.SPECTROGRAM.value)
    allow_regions = BooleanField(u'Allow Regions')
    n_annotations_per_file = IntegerField('Number of annotators per file', default=1, validators=[DataRequired()])
    annotation_tags = FileField(validators=[FileRequired()])
    audio_root_url = StringField('Audio root URL', validators=[DataRequired()])
    audios = FileField(validators=[FileRequired()])

    def __init__(self, *args, **kwargs):
        super(CreateProjectForm, self).__init__(*args, **kwargs)
        #self.feedback_type.choices = [(f.value, f.name) for f in FeedbackType]
        self.visualization_type.choices = [(v.value, v.name) for v in VisualizationType]

    def validate_name(form, field):
        if db.session.query(Project.id).filter_by(name=field.data).scalar() is not None:
            raise ValidationError('Name already used.')

    def validate_annotation_tags(form, field):
        is_empty = True
        for line in form.annotation_tags.data:
            is_empty = False
            if not re.match(r'^[a-zA-Z0-9_\s]+,[a-zA-Z0-9_\s]+$', line.decode().strip()):
                raise ValidationError('Wrong annotation file format.')
        if is_empty:
            raise ValidationError('Annotation file is empty.')
        
    def validate_audios(form, field):
        is_empty = True
        for line in form.audios.data:
            is_empty = False
            if not re.match(r'.+(wav|mp3)$', line.decode().strip()):
                raise ValidationError('Wrong audio list file format.')
        if is_empty:
            raise ValidationError('Audio list file is empty.')

class GetAnnotationsForm(FlaskForm):

    project = SelectField(u'Project', coerce=int)

    def __init__(self, *args, **kwargs):
        super(GetAnnotationsForm, self).__init__(*args, **kwargs)
        self.project.choices = [(p.id, "{}{}".format(p.name, " (completed)" if p.is_completed else "")) for p in Project.query.all()]
