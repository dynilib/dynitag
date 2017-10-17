from flask import redirect, request, jsonify, flash
from flask_admin import AdminIndexView, expose
from flask_login import login_required, current_user


from audiolabeling import app
from audiolabeling.admin.forms import CreateProjectForm, GetAnnotationsForm
from audiolabeling.models import Project


class MyHomeView(AdminIndexView):
    @expose('/')
    def index(self):
        createproject_form = CreateProjectForm()
        getannotations_form = GetAnnotationsForm()
        return self.render('admin/index.html',
                           createproject_form=createproject_form,
                           getannotations_form=getannotations_form)


@app.route('/get_annotations', methods=['POST'])
@login_required
def get_annotations():

    print("in get annotations")
    print(request.form)
    form = GetAnnotationsForm(request.form)

    project_id = form.project.data

    print("User: " + current_user.email)
    print("Project id: " + str(project_id))

    project = Project.query.get(project_id)

    data = {"project": project.name}

    return jsonify(data)

