from hermes_server.app import db
from hermes_server.models.project import Project
from hermes_server.services.exceptions import ValidationError, NotFoundError


class ProjectService:
    @staticmethod
    def list_projects(page=1, per_page=10, name=None):
        query = Project.query.filter(Project.is_active == True)
        if name:
            query = query.filter(Project.name.ilike(f'%{name}%'))
        query = query.order_by(Project.created_at.desc())
        return query

    @staticmethod
    def create_project(name, description=None, owner_id=None):
        if not name:
            raise ValidationError('name is required')

        project = Project(name=name, description=description, owner_id=owner_id)
        db.session.add(project)
        db.session.commit()
        return project

    @staticmethod
    def get_project(project_id):
        project = db.session.get(Project, project_id)
        if not project or not project.is_active:
            raise NotFoundError('project not found')
        return project

    @staticmethod
    def update_project(project_id, **kwargs):
        project = ProjectService.get_project(project_id)

        if 'name' in kwargs:
            project.name = kwargs['name']
        if 'description' in kwargs:
            project.description = kwargs['description']

        db.session.commit()
        return project

    @staticmethod
    def delete_project(project_id):
        project = ProjectService.get_project(project_id)
        project.is_active = False
        db.session.commit()
