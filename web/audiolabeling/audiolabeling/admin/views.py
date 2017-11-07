import os
import uuid
import re

from flask import redirect, request, jsonify, flash, url_for, Markup, Response
from wtforms import Form
from wtforms.validators import ValidationError
import flask_admin
from sqlalchemy import exc, and_
from flask_admin.contrib.sqla import ModelView
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from audiolabeling import app, db, login_manager
from audiolabeling.admin.forms import GetAnnotationsForm
from audiolabeling.models import Project, Audio, AnnotationTag, TagType, FeedbackType, VisualizationType, User, Annotation
from audiolabeling.admin.fields import CustomAdminConverter


class MyHomeView(flask_admin.AdminIndexView):
    @flask_admin.expose('/')
    def index(self):
        getannotations_form = GetAnnotationsForm()
        return self.render('admin/index.html',
                           getannotations_form=getannotations_form)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role=="admin"

    def inaccessible_callback(self, name, **kwargs):
        flash('Only admins can access Admin.', 'error')
        # redirect to login page if user doesn't have access
        return redirect(url_for(login_manager.login_view, next=request.url))


class AdminModelView(ModelView):
    model_form_converter = CustomAdminConverter
    column_labels = dict(name='Name', visualizationtype='Visualization Type',
                         feedbacktype='Feedback Type', allowRegions='Allow Regions',
                         n_annotations_per_file='Number of annotations per file',
                         audios_filename='Audio list filename',
                         annotations_filename='Annotations filename')
    
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role=="admin"

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for(login_manager.login_view, next=request.url))


def random_name(obj, file_data):
    return str(uuid.uuid4()) + ".csv"


def validate_annotationtags(form, field):
    data = field.data
    if data and isinstance(data, FileStorage):
        is_empty = True
        for line in data:
            is_empty = False
            if not re.match(r'^[a-zA-Z0-9_\s]+,[a-zA-Z0-9_\s]+$', line.decode().strip()):
                raise ValidationError('Wrong annotation file format.')
        data.stream.seek(0) # needed to parse it later
        if is_empty:
            raise ValidationError('Annotation file is empty.')


def validate_audios(form, field):
    data = field.data
    if data and isinstance(data, FileStorage):
        is_empty = True
        for line in data:
            is_empty = False
            if not re.match(r'.+(wav|mp3)$', line.decode().strip()):
                raise ValidationError('Wrong audio list file format.')
        data.stream.seek(0) # needed to parse it later
        if is_empty:
            raise ValidationError('Audio list file is empty.')


class ProjectAdminView(AdminModelView):    

    form_excluded_columns = ['feedbacktype', 'audios', 'annotations']


    def scaffold_form(self):
        form_class = super(ProjectAdminView, self).scaffold_form()
        form_class.audios_filename = flask_admin.form.FileUploadField(
            base_path=os.path.join(app.config['UPLOAD_DIR'], 'audios'),
            allow_overwrite=False,
            namegen=random_name,
            validators=[validate_audios])
        form_class.annotations_filename = flask_admin.form.FileUploadField(
            base_path=os.path.join(app.config['UPLOAD_DIR'], 'annotations'),
            allow_overwrite=False,
            namegen=random_name,
            validators=[validate_annotationtags])
        return form_class


    def on_model_change(self, form, project, is_created):

        audios_file = form.audios_filename.data
        annotations_file = form.annotations_filename.data

        if audios_file and isinstance(audios_file, FileStorage):

            if not is_created:
                # delete audio-project relationships
                project.audios = []
                self.session.add(project)

            audios_file.stream.seek(0) # I need it here. Why ?
            for line in audios_file:
                rel_path = line.decode().strip()
                audio = Audio.query.filter(Audio.rel_path==rel_path).first()
                if not audio:
                    audio = Audio()
                    audio.rel_path = line.decode().strip()
                project.audios.append(audio)
            audios_file.stream.seek(0) # needed to save it all

            if not is_created:
                # delete orphan audios
                self.session.query(Audio).\
                    filter(~Audio.projects.any()).\
                    delete(synchronize_session=False)

        if annotations_file and isinstance(annotations_file, FileStorage):

            if not is_created:
                # delete annotationtag-project relationships
                project.annotationtags = []
                self.session.add(project)

            annotations_file.stream.seek(0) # I need it here. Why ?
            for line in annotations_file:
                tagtype_name, anntag_name = line.decode().split(',')
                tagtype = TagType.query.filter(TagType.name==tagtype_name).first()
                if not tagtype:
                    tagtype = TagType()
                    tagtype.name = tagtype_name
                    self.session.add(tagtype)
                    self.session.commit()
                anntag = AnnotationTag.query.filter(AnnotationTag.name==anntag_name).filter(AnnotationTag.tagtype_id==tagtype.id).first()
                if not anntag:
                    anntag = AnnotationTag()
                    anntag.name = anntag_name
                    anntag.tagtype_id = tagtype.id
                project.annotationtags.append(anntag)
            annotations_file.stream.seek(0) # needed to save it all

            if not is_created:
                # delete orphan annotation tags
                self.session.query(AnnotationTag).\
                    filter(~AnnotationTag.projects.any()).\
                    delete(synchronize_session=False)

        self.session.commit()


@app.route('/get_annotations', methods=['GET'])
@login_required
def get_annotations():

    form = GetAnnotationsForm(request.args)

    project_id = form.project.data
    project = Project.query.get(project_id)

    audios = []
    for audio in project.audios:
        annotations = []
        for ann in Annotation.query.filter(and_(Annotation.project_id==project_id, Annotation.audio_id==audio.id)):
            annotations.append({
                "id": ann.id,
                "annotationtag_id": ann.annotationtag_id,
                "user_id": ann.user_id
            })
            if project.allowRegions:
                annotations[-1]["start_time"] = ann.start_time
                annotations[-1]["end_time"] = ann.end_time
        audios.append({
            "id": audio.id,
            "rel_path": audio.rel_path,
            "annotations": annotations
        })

    users = User.query.join(Annotation).filter(Annotation.project_id==project_id).all()
    annotationtags = AnnotationTag.query.filter(AnnotationTag.projects.any(Project.id==project_id)).all()

    data = {
        "users": [{"id": u.id, "name": u.username, "email": u.email} for u in users],
        "annotation_tags": [{"id": a.id, "name": a.name, "tagtype_name": a.tagtype.name} for a in annotationtags],
        "project": project.name,
        "audio_root_url": project.audio_root_url,
        "audios": audios
    }

    response = jsonify(data)
    response.headers['Content-Disposition'] = 'attachment;filename={}_annotations.json'.format(re.sub(r'[^a-zA-Z0-9_]','_', project.name))
    return response
