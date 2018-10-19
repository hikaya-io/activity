import django_tables2 as tables
from models import ProjectAgreement

TEMPLATE = '''
<div class="btn-group btn-group-xs">
   <a type="button" class="btn btn-warning" href="/workflow/projectagreement_update/{{ record.id }}">Edit</a>
   <a type="button" class="btn btn-default" href="/workflow/projectagreement_detail/{{ record.id }}">View</a>
</div>
'''


class ProjectAgreementTable(tables.Table):
    edit = tables.TemplateColumn(TEMPLATE)
    total_cost = tables.Column(accessor='projectcomplete.actual_budget',verbose_name="Total Cost")

    class Meta:
        model = ProjectAgreement
        attrs = {"class": "paleblue"}
        fields = ('program', 'project_name','sites', 'activity_code', 'office', 'project_name', 'sector', 'project_activity',
                             'project_type', 'account_code', 'lin_code','estimated_by','total_estimated_budget','mc_estimated_budget','total_cost')
        sequence = ('program', 'project_name','sites', 'activity_code', 'office', 'project_name', 'sector', 'project_activity',
                             'project_type', 'account_code', 'lin_code','estimated_by','total_estimated_budget','mc_estimated_budget','total_cost')

TEMPLATE2 = '''
   <a class="btn btn-default btn-xs" role="button" href="/incident/{{ record.id }}/print">Print</a>
'''