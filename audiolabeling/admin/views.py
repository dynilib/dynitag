import os
import uuid

from flask import redirect, request, jsonify, flash, url_for, Markup
import flask_admin
from sqlalchemy import exc
from flask_admin.contrib.sqla import ModelView
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from audiolabeling import app, db, login_manager
from audiolabeling.admin.forms import CreateProjectForm, GetAnnotationsForm
from audiolabeling.models import Project, Audio, AnnotationTag, TagType, FeedbackType, VisualizationType
from audiolabeling.admin.fields import CustomAdminConverter


class MyHomeView(flask_admin.AdminIndexView):
    @flask_admin.expose('/')
    def index(self):
        createproject_form = CreateProjectForm()
        getannotations_form = GetAnnotationsForm()
        return self.render('admin/index.html',
                           createproject_form=createproject_form,
                           getannotations_form=getannotations_form)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role=="admin"

    def inaccessible_callback(self, name, **kwargs):
        flash('Only admins can access Admin.', 'error')
        # redirect to login page if user doesn't have access
        return redirect(url_for(login_manager.login_view, next=request.url))


class AdminModelView(ModelView):
    model_form_converter = CustomAdminConverter
    
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role=="admin"

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for(login_manager.login_view, next=request.url))


@app.route('/create_project', methods=['POST'])
@login_required
def create_project():

    form = CreateProjectForm() # FlaskForm implicitely pass the request data to the form

    if form.validate_on_submit():

        try:

            project = Project()
            project.name = form.name.data
            project.audio_root_url = form.audio_root_url.data
            project.allowRegions = form.allow_regions.data
            project.visualizationtype = VisualizationType(form.visualization_type.data)

            audios_file = form.audios.data
            audios_filename = str(uuid.uuid4()) + ".csv"
            project.audios_filename = audios_filename
            for line in audios_file:
                rel_path = line.decode().strip()
                audio = Audio.query.filter(Audio.rel_path==rel_path).first()
                if not audio:
                    audio = Audio()
                    audio.rel_path = line.decode().strip()
                project.audios.append(audio)
            audios_file.stream.seek(0) # needed to save it all
            audios_file.save(os.path.join(
                app.config['UPLOAD_DIR'], 'audios', audios_filename
            ))


            annotations_file = form.annotation_tags.data
            annotations_filename = str(uuid.uuid4()) + ".csv"
            project.annotations_filename = annotations_filename
            for line in annotations_file:
                tagtype_name, anntag_name = line.decode().split(',')
                tagtype = TagType.query.filter(TagType.name==tagtype_name).first()
                if not tagtype:
                    tagtype = TagType()
                    tagtype.name = tagtype_name
                    db.session.add(tagtype)
                    db.commit()
                anntag = AnnotationTag.query.filter(AnnotationTag.name==anntag_name).first()
                if not anntag:
                    anntag = AnnotationTag()
                    anntag.name = anntag_name
                    anntag.tagtype_id = tagtype.id
                project.annotationtags.append(anntag)
            annotations_file.stream.seek(0) # needed to save it all
            annotations_file.save(os.path.join(
                app.config['UPLOAD_DIR'], 'annotations', annotations_filename
            ))

            db.session.add(project)
            db.session.commit()
            
            flash(
                Markup("Project created. You can edit it <a href=\"{}\">here</a>.".format(
                    url_for('project.index_view', id=1))),
                "success");
            
            return '', 200

        except exc.IntegrityError as e:
            db.session.rollback()
#            return jsonify({'errors': })

    else:
        return jsonify({'errors': form.errors})


@app.route('/get_annotations', methods=['POST'])
@login_required
def get_annotations():

    form = GetAnnotationsForm(request.form)

    project_id = form.project.data

    project = Project.query.get(project_id)


    audios = []
    for audio in project.audios:
        annotations = []
        for ann in audio.annotations:
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


    data = {
        "project": project.name,
        "audio_root_url": project.audio_root_url,
        "audios": audios
    }

    return jsonify(data)



