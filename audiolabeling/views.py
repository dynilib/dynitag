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

    print("User: " + current_user.email)
    print("Project id: " + project_id)

    # get random audio from project with no annotations from current user
    audio = Audio.query.order_by(func.random())\
        .filter(Audio.project_id==project_id)\
        .filter(~Audio.annotations.any(Annotation.user_id==1))\
        .first()

    if audio:

        proj = Project.query.get(project_id)
        annotation_tags = AnnotationTag.query.filter(project_id==project_id)
        tagtypes = annotation_tags.with_entities(TagType).all()

        data = {}

        data["feedback"] = proj.feedbacktype.value
        data["visualization"] = proj.visualizationtype.value
        data["annotationTags"] = {}
        for tagtype in tagtypes:
            data["annotationTags"][tagtype.name] = [ann_tag.name for ann_tag in annotation_tags.filter(AnnotationTag.tagtype==tagtype).all()]
        data["url"] = url_for("static", filename=audio.url)
        data["tutorialVideoURL"] = "https://www.youtube.com/embed/Bg8-83heFRM"
        data["alwaysShowTags"] = True
        data["instructions"] = [
                        "Highlight &amp; Label Each Sound",
                        "1. &nbsp; Familiarize yourself with the list of sound labels under the audio recording.", 
                        "2. &nbsp; Click the play button and listen to the recording.", 
                        "3. &nbsp; For each sound event that you hear click and drag on the visualization to create a new annotation.",
                        "4. &nbsp; When creating a new annotation be as precise as possible.",
                        "5. &nbsp; Select the appropriate label and indicate whether the sound is near or far."
                    ]

    return jsonify({"task": data})


@app.route('/post_annotation', methods=['POST'])
@login_required
def post_annotation():

    print("****in post_annotation***")

    data = request.json
    print(data)

    for ann in data["annotations"]:
        annotation = Annotation()
        annotation.annotationtag_id = 1 # TODO
        annotation.audio_id = 1 # TODO
        db.session.add(annotation)
        db.session.commit()
        # TODO commit manage error
        flash('New annotation, added!', 'success')
        return jsonify({'success':True}), 200, {'ContentType':'application/json'} 
