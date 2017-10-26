import os
from flask import render_template, redirect, request, jsonify, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy.sql.expression import func

from . import app, db
from .models import Project, AnnotationTag, Audio, Annotation, TagType
from .forms import ProjectForm

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
    form = ProjectForm()
    if request.method == 'POST':
        project_id = form.project.data
        return redirect(url_for('project', project_id=project_id))
    return render_template('projects.html', form=form)


@app.route('/project/<project_id>')
@login_required
def project(project_id):
    get_url = '/get_task/' + str(project_id)
    post_url = '/post_annotation'
    return render_template('project.html',
                           get_url=get_url,
                           post_url = post_url)

#
#
#	form = ProjectForm(request.POST)
#    if request.method == 'POST' and form.validate():
#        project = form.project.data
#        redirect(url_for('task', project=project))
#    return render_response('projects.html', form=form)


@app.route('/get_task/<project_id>', methods=['GET', 'POST'])
@login_required
def get_task(project_id):

    proj = Project.query.get(project_id)

    # Get audios from current project that have not been annotated by the current user
    query = Audio.query.filter(Audio.projects.any(Project.id==project_id))\
        .filter(~Audio.annotations.any(Annotation.user_id==current_user.id))

    # Get the audio with annotations from proj.n_annotations_per_file users or more to filter the query
    if proj.n_annotations_per_file:
        subquery = db.session.query(Audio, db.func.count(Annotation.user_id.distinct()).label('count_users')).join(Audio.annotations).group_by(Audio.id).subquery()
        subquery = db.session.query(subquery.c.id).filter(subquery.c.count_users >= proj.n_annotations_per_file)
        query = query.filter(Audio.id.notin_(subquery))

    audio = query.order_by(func.random()).first()

    if audio:

        data = {}

        annotation_tags = proj.annotationtags
        tagtypes = annotation_tags.with_entities(TagType).all()

        data["project_id"] = project_id
        data["audio_id"] = audio.id
        data["feedback"] = proj.feedbacktype.name.lower()
        data["visualization"] = proj.visualizationtype.name.lower()
        data["allowRegions"] = proj.allowRegions
        data["annotationTags"] = {}
        for tagtype in tagtypes:
            data["annotationTags"][tagtype.name] = [ann_tag.name for ann_tag in annotation_tags.filter(AnnotationTag.tagtype==tagtype).all()]
        data["url"] = os.path.join(proj.audio_root_url, audio.rel_path)
        data["tutorialVideoURL"] = "https://www.youtube.com/embed/Bg8-83heFRM"
        data["alwaysShowTags"] = True

        if proj.allowRegions:
            data["instructions"] = [
                            "Highlight &amp; Label Each Sound",
                            "1. &nbsp; Familiarize yourself with the list of sound labels under the audio recording.", 
                            "2. &nbsp; Click the play button and listen to the recording.", 
                            "3. &nbsp; For each sound event that you hear click and drag on the visualization to create a new annotation.",
                            "4. &nbsp; When creating a new annotation be as precise as possible.",
                        ]
        else:
            data["instructions"] = [
                            "Highlight &amp; Label Each Sound",
                            "1. &nbsp; Familiarize yourself with the list of sound labels under the audio recording.", 
                            "2. &nbsp; Click the play button and listen to the recording.", 
                            "3. &nbsp; Make sure the correct annotations are selected before submitting.",
                        ]
        return jsonify({"task": data})

    return jsonify({"message": "Your annotation task for project {} is over ! Select another project <a href=\"{}\">here</a>.".format(proj.name, url_for('projects'))})


@app.route('/post_annotation', methods=['POST'])
@login_required
def post_annotation():

    data = request.json

    audio_id = data["audio_id"]
    project_id = data["project_id"]
    project = Project.query.get(project_id)

    for region in data["annotations"]:

        start_time = region["start"]
        end_time = region["end"]

        for _, v in region["annotations"].items():
            
            ann = Annotation()
            ann.annotationtag_id = AnnotationTag.query.filter(AnnotationTag.name==v)[0].id
            ann.audio_id = audio_id
            ann.project_id = project_id
            ann.user_id = current_user.id
            if project.allowRegions:
                ann.start_time = start_time
                ann.end_time = end_time
            db.session.add(ann)
            db.session.commit()
            # TODO commit manage error
    
    return (
        jsonify({
            'success':True,
            'flash_message':{'msg': 'New annotation, added!', 'cat': 'success'}}),
        200,
        {'ContentType':'application/json'})

