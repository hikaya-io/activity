from import_export import resources
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from import_export import fields
from .models import ProjectAgreement, Program, SiteProfile, Capacity, Evaluate, Documentation,\
    Stakeholder, Sector, ProjectType, Office, TolaUser, ProjectComplete, Country, Contact, StakeholderType, TolaUserProxy


class ProjectAgreementResource(resources.ModelResource):
    site = fields.Field(column_name='site', attribute='site', widget=ManyToManyWidget(SiteProfile, 'name'))
    capacity = fields.Field(column_name='capacity', attribute='capacity', widget=ManyToManyWidget(Capacity, 'capacity'))
    evaluate = fields.Field(column_name='evaluate', attribute='evaluate', widget=ManyToManyWidget(Evaluate, 'evaluate'))
    stakeholder = fields.Field(column_name='stakeholder', attribute='stakeholder', widget=ManyToManyWidget(Stakeholder, 'name'))
    program = fields.Field(column_name='program', attribute='program', widget=ForeignKeyWidget(Program, 'name'))
    sector = fields.Field(column_name='sector', attribute='sector', widget=ForeignKeyWidget(Sector, 'sector'))
    project_type = fields.Field(column_name='project_type', attribute='project_type', widget=ForeignKeyWidget(ProjectType, 'name'))
    office = fields.Field(column_name='office', attribute='office', widget=ForeignKeyWidget(Office, 'code'))
    estimated_by = fields.Field(column_name='estimated_by', attribute='estimated_by', widget=ForeignKeyWidget(TolaUser, 'name'))
    approved_by = fields.Field(column_name='approved_by', attribute='approved_by', widget=ForeignKeyWidget(TolaUser, 'name'))

    class Meta:
        model = ProjectAgreement


class ProjectCompleteResource(resources.ModelResource):
    site = fields.Field(column_name='site', attribute='site', widget=ManyToManyWidget(SiteProfile, 'name'))
    capacity = fields.Field(column_name='capacity', attribute='capacity', widget=ManyToManyWidget(Capacity, 'capacity'))
    evaluate = fields.Field(column_name='evaluate', attribute='evaluate', widget=ManyToManyWidget(Evaluate, 'evaluate'))
    stakeholder = fields.Field(column_name='stakeholder', attribute='stakeholder', widget=ManyToManyWidget(Stakeholder, 'name'))
    program = fields.Field(column_name='program', attribute='program', widget=ForeignKeyWidget(Program, 'name'))
    sector = fields.Field(column_name='sector', attribute='sector', widget=ForeignKeyWidget(Sector, 'sector'))
    project_type = fields.Field(column_name='project_type', attribute='project_type', widget=ForeignKeyWidget(ProjectType, 'name'))
    office = fields.Field(column_name='office', attribute='office', widget=ForeignKeyWidget(Office, 'code'))
    estimated_by = fields.Field(column_name='estimated_by', attribute='estimated_by', widget=ForeignKeyWidget(TolaUser, 'name'))
    approved_by = fields.Field(column_name='approved_by', attribute='approved_by', widget=ForeignKeyWidget(TolaUser, 'name'))

    class Meta:
        model = ProjectComplete


class ProgramResource(resources.ModelResource):

    class Meta:
        model = Program

class StakeholderResource(resources.ModelResource):
    type = fields.Field(column_name='type', attribute='type', widget=ForeignKeyWidget(StakeholderType, 'name'))
    contact = fields.Field(column_name='contact', attribute='contact', widget=ManyToManyWidget(Contact, field='name'))
    country = fields.Field(column_name='country', attribute='country', widget=ForeignKeyWidget(Country, 'country'))
    sectors = fields.Field(column_name='sectors', attribute='sectors', widget=ManyToManyWidget(Sector, field='sector'))
    approved_by = fields.Field(column_name='approved_by', attribute='approved_by', widget=ForeignKeyWidget(TolaUser, 'name'))
    filled_by = fields.Field(column_name='filled_by', attribute='filled_by', widget=ForeignKeyWidget(TolaUser, 'name'))
    stakeholder_register = fields.Field(column_name='stakeholder_register', attribute='stakeholder_register')
    formal_relationship_document = fields.Field(column_name='formal_relationship_document', attribute='formal_relationship_document', widget=ForeignKeyWidget(Documentation, 'name_n_url'))
    vetting_document = fields.Field(column_name='vetting_document', attribute='vetting_document', widget=ForeignKeyWidget(Documentation, 'name_n_url'))

    class Meta:
        model = Stakeholder

    def dehydrate_stakeholder_register(self, stakeholder):
        if stakeholder.stakeholder_register == 1:

            return 'True'

        if stakeholder.stakeholder_register == 0:

            return 'False'


