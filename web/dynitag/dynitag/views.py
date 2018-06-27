import os
from flask import render_template, redirect, request, jsonify, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy.sql.expression import func
from sqlalchemy import and_

from dynitag import app, db
from dynitag.models import Project, AnnotationTag, Audio, Annotation, TagType
from dynitag.forms import ProjectForm

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
    proj = Project.query.get(project_id)
    allow_regions = 'true' if proj.allowRegions else 'false'
    return render_template('project.html',
                           get_url=get_url,
                           post_url=post_url,
                           allow_regions=allow_regions)


@app.route('/get_task/<project_id>', methods=['GET', 'POST'])
@login_required
def get_task(project_id):

    proj = Project.query.get(project_id)

    # Get audios from current project that have not been annotated by the current user
    query = Audio.query.filter(Audio.projects.any(Project.id==project_id))\
        .filter(~Audio.annotations.any(and_(Annotation.user_id==current_user.id, Annotation.project_id==project_id)))

    # Get the audio with annotations from proj.n_annotations_per_file users or more to filter the query
    if proj.n_annotations_per_file:
        subquery = db.session.query(Audio, db.func.count(Annotation.user_id.distinct()).label('count_users')).join(Audio.annotations).group_by(Audio.id).subquery()
        subquery = db.session.query(subquery.c.id).filter(subquery.c.count_users >= proj.n_annotations_per_file)
        query = query.filter(Audio.id.notin_(subquery))

    audio = query.order_by(func.random()).first()

    if audio:

        data = {}

        annotation_tags = proj.annotationtags
        tagtypes = db.session.query(TagType).join(AnnotationTag).filter(AnnotationTag.projects.any(Project.id==project_id)).all()

        data["project_id"] = project_id
        data["audio_id"] = audio.id
        data["feedback"] = proj.feedbacktype.name.lower()
        data["visualization"] = proj.visualizationtype.name.lower()
        data["annotationTypes"] = {}
        data["annotationTags"] = {}
        for tagtype in tagtypes:
            data["annotationTypes"][tagtype.id] = tagtype.name
            data["annotationTags"][tagtype.id] = [ann_tag.name for ann_tag in annotation_tags.filter(AnnotationTag.tagtype==tagtype).all()]
        data["url"] = os.path.join(proj.audio_root_url, audio.rel_path)
        data["tutorialVideoURL"] = "https://www.youtube.com/embed/Bg8-83heFRM"
        data["alwaysShowTags"] = True

        # stats
#        n_tagtypes = db.session.query(db.func.count(AnnotationTag.tagtype_id.distinct())).filter(Project.id==project_id).join(Project.annotationtags).group_by(Project.id).one()[0]
#        data["stats"] = "You annotated {} files. Total number of annotations: {} / {} ({} files, {} annotation(s) per file needed)"\
#            .format(
#                int(proj.annotations.filter(Annotation.user_id==current_user.id).count() / n_tagtypes),
#                int(proj.annotations.count() / n_tagtypes),
#                proj.audios.count() * (proj.n_annotations_per_file if proj.n_annotations_per_file else 1),
#                proj.audios.count(),
#                proj.n_annotations_per_file if proj.n_annotations_per_file else 1
#            )

        n_annotated_files = Audio.query.filter(Audio.projects.any(Project.id==project_id)) \
                .filter(Audio.annotations.any(and_(Annotation.user_id==current_user.id,
                            Annotation.project_id==project_id))).count()
        n_annotations = proj.annotations.filter(Annotation.user_id==current_user.id).count()
        n_annotators = proj.n_annotations_per_file if proj.n_annotations_per_file else 1

        data["stats"] = "You annotated {} files, with {} annotations. (Total ".format(
                n_annotated_files, n_annotations) +\
                        "number of files : {}. Number of annotators per file ".format(proj.audios.count()) +\
                        "needed: {})".format(n_annotators)

        if proj.allowRegions:
            data["instructions"] = [
                            "Highlight &amp; Label Each Sound",
                            "1. &nbsp; Familiarize yourself with the list of sound labels under the audio recording.", 
                            "2. &nbsp; Click the play button and listen to the recording.", 
                            "3. &nbsp; For each sound event that you hear click and drag on the visualization to create a new annotation segment.",
                            "4. &nbsp; When creating a new annotation segment be as precise as possible.",
                            "5. &nbsp; Make sure the correct annotation tags are selected before submitting.",
                        ]
        else:
            data["instructions"] = [
                            "Highlight &amp; Label Each Sound",
                            "1. &nbsp; Familiarize yourself with the list of sound labels under the audio recording.", 
                            "2. &nbsp; Click the play button and listen to the recording.", 
                            "3. &nbsp; Make sure the correct annotation tags are selected before submitting.",
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

        for tagtype_id, tag_name in region["annotations"].items():
            
            ann = Annotation()
            ann.annotationtag_id = AnnotationTag.query.filter(and_(AnnotationTag.name==tag_name, AnnotationTag.tagtype_id==tagtype_id)).first().id
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

