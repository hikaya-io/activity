#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.views.generic.list import ListView
from django.http import HttpResponse

from django.shortcuts import render
from workflow.models import ProjectAgreement, ProjectComplete, Program, \
    SiteProfile, Country, ActivitySites
from .models import ProgramNarratives, JupyterNotebooks
from formlibrary.models import TrainingAttendance, Distribution, Beneficiary
from indicators.models import CollectedData, Indicator, ActivityTable

from django.db.models import Sum
from django.db.models import Q

from activity.util import get_country, get_table

from django.contrib.auth.decorators import login_required
import requests
import json
import ast


class ProgramList(ListView):
    """
    List of Programs with links to the dashboards
    http://127.0.0.1:8000/customdashboard/program_list/0/
    """
    model = Program
    template_name = 'customdashboard/program_list.html'

    def get(self, request, *args, **kwargs):

        # retrieve the coutries the user has data access for
        country = None
        countries = get_country(request.user)
        country_list = Country.objects.all().filter(id__in=countries)
        organization = request.user.activity_user.organization
        if int(self.kwargs['pk']) == 0:
            get_program = Program.objects.all().filter(
                organization=organization)
        else:
            get_program = Program.objects.all().filter(
                country__id=self.kwargs['pk'])
            country = Country.objects.get(id=self.kwargs['pk']).country

        program_list = []
        for program in get_program:
            # get the percentage of indicators with data
            get_indicator_data_count = Indicator.objects.filter(
                program__id=program.id).exclude(
                collecteddata__periodic_target=None).count()
            get_indicator_count = Indicator.objects.filter(
                program__id=program.id).count()
            if get_indicator_count > 0 and get_indicator_data_count > 0:
                get_indicator_data_percent = \
                    100 * float(get_indicator_data_count) / float(
                        get_indicator_count)
            else:
                get_indicator_data_percent = 0

            program.indicator_data_percent = int(get_indicator_data_percent)
            program.indicator_percent = int(100 - get_indicator_data_percent)

            # get the percentage of projects with completes (tracking)
            get_project_agreement_count = ProjectAgreement.objects.filter(
                program__id=program.id).count()
            get_project_complete_count = ProjectComplete.objects.filter(
                program__id=program.id).count()
            if get_project_agreement_count > 0 and \
                    get_project_complete_count > 0:
                project_percent = 100 * \
                                  float(get_project_complete_count) / \
                                  float(get_project_agreement_count)
            else:
                project_percent = 0

            # append the rounded percentages to the program list
            program.project_percent = int(project_percent)
            program.project_agreement_percent = int(100 - project_percent)
            program_list.append(program)

        return render(request, self.template_name,
                      {'get_program': program_list, 'get_country': country_list,
                       'country': country})


@login_required(login_url='/accounts/login/')
def default_custom_dashboard(request, id=0, status=0):
    """
    This is used as the workflow program dashboard
    # of agreements, approved, rejected, waiting,
        archived and total for dashboard
    http://127.0.0.1:8000/customdashboard/65/
    """
    program_id = id
    countries = get_country(request.user)

    # transform to list if a submitted country
    selected_countries_list = Country.objects.all().filter(
        program__id=program_id)

    get_quantitative_data_sums = CollectedData.objects.filter(
        indicator__program__id=program_id, achieved__isnull=False,
        indicator__key_performance_indicator=True) \
        .exclude(achieved=None).order_by(
        'indicator__number').values('indicator__number', 'indicator__name',
                                    'indicator__id') \
        .annotate(targets=Sum('periodic_target__target'),
                  actuals=Sum('achieved')).exclude(achieved=None)

    total_targets = get_quantitative_data_sums.aggregate(Sum('targets'))
    total_actuals = get_quantitative_data_sums.aggregate(Sum('actuals'))

    get_filtered_name = Program.objects.get(id=program_id)

    get_projects_count = ProjectAgreement.objects.all().filter(
        program__id=program_id, program__country__in=countries).count()
    get_budget_estimated = ProjectAgreement.objects.all().filter(
        program__id=program_id, program__country__in=countries).annotate(
        estimated=Sum('total_estimated_budget'))
    get_awaiting_approval_count = ProjectAgreement.objects.all().filter(
        program__id=program_id, approval='awaiting approval',
        program__country__in=countries).count()
    get_approved_count = ProjectAgreement.objects.all().filter(
        program__id=program_id, approval='approved',
        program__country__in=countries).count()
    get_rejected_count = ProjectAgreement.objects.all().filter(
        program__id=program_id, approval='rejected',
        program__country__in=countries).count()
    get_in_progress_count = ProjectAgreement.objects.all().filter(
        program__id=program_id).filter(
        Q(Q(approval='in progress') | Q(approval=None)),
        program__country__in=countries).count()
    no_status_count = ProjectAgreement.objects.all().filter(
        program__id=program_id).filter(
        Q(Q(approval=None) | Q(approval=""))).count()

    get_site_profile = SiteProfile.objects.all().filter(
        Q(projectagreement__program__id=program_id) | Q(
            collecteddata__program__id=program_id))
    get_site_profile_indicator = SiteProfile.objects.all().filter(
        Q(collecteddata__program__id=program_id))

    if status == 'Approved':
        get_projects = ProjectAgreement.objects.all().filter(
            program__id=program_id,
            program__country__in=countries,
            approval='approved').prefetch_related('projectcomplete')
    elif status == 'Rejected':
        get_projects = ProjectAgreement.objects.all().filter(
            program__id=program_id,
            program__country__in=countries,
            approval='rejected').prefetch_related('projectcomplete')
    elif status == 'In Progress':
        get_projects = ProjectAgreement.objects.all().filter(
            program__id=program_id,
            program__country__in=countries,
            approval='in progress').prefetch_related('projectcomplete')
    elif status == 'Awaiting Approval':
        get_projects = ProjectAgreement.objects.all().filter(
            program__id=program_id, program__country__in=countries,
            approval='awaiting approval').prefetch_related('projectcomplete')
    else:
        get_projects = ProjectAgreement.objects.all().filter(
            program__id=program_id, program__country__in=countries)

    get_project_completed = []

    total_budgetted = 0.00
    total_actual = 0.00

    get_projects_complete = ProjectComplete.objects.all()
    for project in get_projects:
        for complete in get_projects_complete:
            if complete.actual_budget is not None:
                if project.id == complete.project_agreement_id:
                    total_budgetted = float(
                        total_budgetted) + float(
                        project.total_estimated_budget)
                    total_actual = float(total_actual) + \
                                   float(complete.actual_budget)

                    get_project_completed.append(project)

    return render(request,
                  "customdashboard/customdashboard/visual_dashboard.html",
                  {'get_site_profile': get_site_profile,
                   'get_budget_estimated': get_budget_estimated,
                   'get_quantitative_data_sums': get_quantitative_data_sums,
                   'country': countries,
                   'get_awaiting_approval_count': get_awaiting_approval_count,
                   'get_filtered_name': get_filtered_name,
                   'get_projects': get_projects,
                   'get_approved_count': get_approved_count,
                   'get_rejected_count': get_rejected_count,
                   'get_in_progress_count': get_in_progress_count,
                   'nostatus_count': no_status_count,
                   'get_projects_count': get_projects_count,
                   'selected_countries_list': selected_countries_list,
                   'get_site_profile_indicator': get_site_profile_indicator,
                   'get_project_completed': get_project_completed,
                   'total_actuals': total_actuals,
                   'total_targets': total_targets,
                   'total_budgetted': total_budgetted,
                   'total_actual': total_actual})


def public_dashboard(request, id=0, public=0):
    """
    This is used as the internal and external (public) dashboard view
    the template is changed for public
    :public: if URL contains a 0 then show the internal dashboard
    if 1 then public dashboard
    http://127.0.0.1:8000/customdashboard/program_dashboard/65/0/
    """
    program_id = id
    get_quantitative_data_sums_2 = CollectedData.objects.all().filter(
        indicator__program__id=program_id, achieved__isnull=False) \
        .order_by('indicator__source').values('indicator__number',
                                              'indicator__source',
                                              'indicator__id')
    get_quantitative_data_sums = CollectedData.objects.filter(
        indicator__program__id=program_id, achieved__isnull=False).exclude(
        achieved=None) \
        .order_by('indicator__number').values('indicator__number',
                                              'indicator__name',
                                              'indicator__id') \
        .annotate(targets=Sum('periodic_target__target'),
                  actuals=Sum('achieved'))
    get_indicator_count = Indicator.objects.all().filter(
        program__id=program_id).count()

    get_indicator_data = CollectedData.objects.all().filter(
        indicator__program__id=program_id, achieved__isnull=False).order_by(
        'date_collected')

    get_indicator_count_data = get_indicator_data.count()

    get_indicator_count_kpi = Indicator.objects.all().filter(
        program__id=program_id, key_performance_indicator=1).count()
    get_program = Program.objects.all().get(id=program_id)
    try:
        get_program_narrative = ProgramNarratives.objects.get(
            program_id=program_id)
    except ProgramNarratives.DoesNotExist:
        get_program_narrative = None
    get_projects = ProjectComplete.objects.all().filter(program_id=program_id)
    get_all_projects = ProjectAgreement.objects.all().filter(
        program_id=program_id)
    get_site_profile = SiteProfile.objects.all().filter(
        projectagreement__program__id=program_id)
    get_site_profile_indicator = SiteProfile.objects.all().filter(
        Q(collecteddata__program__id=program_id))

    get_projects_count = ProjectAgreement.objects.all().filter(
        program__id=program_id).count()
    get_awaiting_approval_count = ProjectAgreement.objects.all().filter(
        program__id=program_id, approval='awaiting approval').count()
    get_approved_count = ProjectAgreement.objects.all().filter(
        program__id=program_id, approval='approved').count()
    get_rejected_count = ProjectAgreement.objects.all().filter(
        program__id=program_id, approval='rejected').count()
    get_in_progress_count = ProjectAgreement.objects.all().filter(
        Q(program__id=program_id) & Q(
            Q(approval='in progress') | Q(approval=None) | Q(
                approval=""))).count()

    no_status_count = ProjectAgreement.objects.all().filter(
        Q(program__id=program_id) & Q(
            Q(approval=None) | Q(approval=""))).count()

    get_notebooks = JupyterNotebooks.objects.all().filter(
        program__id=program_id)

    # get all countries
    countries = Country.objects.all().filter(program__id=program_id)

    # Trainings
    agreement_id_list = []
    training_id_list = []

    # Indicator Evidence
    get_evidence = ActivityTable.objects.all().filter(country__in=countries)
    evidence_tables_count = get_evidence.count()
    evidence_tables = []

    try:
        for table in get_evidence:
            table.table_data = get_table(table.url)

            print(table.table_data)

            evidence_tables.append(table)

    except Exception as e:
        pass

    for p in get_projects:
        agreement_id_list.append(p.id)

    get_trainings = TrainingAttendance.objects.all().filter(
        project_agreement_id__in=agreement_id_list)

    get_distributions = Distribution.objects.all().filter(
        initiation_id__in=agreement_id_list)

    for t in get_trainings:
        training_id_list.append(t.id)

    get_beneficiaries = Beneficiary.objects.all().filter(
        training__in=training_id_list)

    get_project_completed = []

    get_projects_complete = ProjectComplete.objects.all()
    for project in get_projects:
        for complete in get_projects_complete:
            if complete.actual_budget is not None:
                if project.id == complete.project_agreement_id:
                    get_project_completed.append(project)

    # public dashboards have a different template display
    if int(public) == 1:
        print("public")
        template = "customdashboard/publicdashboard/public_dashboard.html"
    else:
        template = "customdashboard/publicdashboard/program_dashboard.html"

    return render(request, template, {
        'get_program': get_program, 'get_projects': get_projects,
        'get_site_profile': get_site_profile, 'countries': countries,
        'get_program_narrative': get_program_narrative,
        'get_awaiting_approval_count': get_awaiting_approval_count,
        'get_quantitative_data_sums_2': get_quantitative_data_sums_2,
        'get_approved_count': get_approved_count,
        'get_rejected_count': get_rejected_count,
        'get_in_progress_count': get_in_progress_count,
        'nostatus_count': no_status_count,
        'total_projects': get_projects_count,
        'get_indicator_count': get_indicator_count,
        'get_indicator_data': get_indicator_data,
        'get_indicator_count_data': get_indicator_count_data,
        'get_indicator_count_kpi': get_indicator_count_kpi,
        'get_evidence': get_evidence, 'evidence_tables': evidence_tables,
        'get_notebooks': get_notebooks,
        'evidence_tables_count': evidence_tables_count,
        'get_quantitative_data_sums': get_quantitative_data_sums,
        'get_site_profile_indicator': get_site_profile_indicator,
        'get_site_profile_indicator_count': get_site_profile_indicator.count(),
        'get_beneficiaries': get_beneficiaries,
        'get_distributions': get_distributions, 'get_trainings': get_trainings,
        'get_project_completed': get_project_completed,
        'get_all_projects': get_all_projects})


"""
Extremely Customized dashboards
This section contains custom dashboards or one-off dashboard for demo, 
or specificcustomer requests outside the scope of customized program dashboards
"""


def survey_public_dashboard(request, id=0):
    """
    DEMO only survey for Activity survey
    :return:
    """

    # get all countires
    countries = Country.objects.all()
    # TODO : change this url
    filter_url = "http://activity-tables.mercycorps.org/api/silo/430/data/"
    token = ActivitySites.objects.get(site_id=1)
    if token.activity_tables_token:
        headers = {'content-type': 'application/json',
                   'Authorization': 'Token ' + token.activity_tables_token}
    else:
        headers = {'content-type': 'application/json'}
        print("Token Not Found")

    response = requests.get(filter_url, headers=headers, verify=False)
    get_json = json.loads(response.content)
    data = ast.literal_eval(get_json)
    meaning = list()
    join = list()
    activity_is = list()
    for item in data['data']:
        print(item['activity_is_a_pashto_word_meaning_'])
        meaning.append(item['activity_is_a_pashto_word_meaning_'])
        # multiple choice
        join.append(
            list(x for x in item[
                'thanks_for_coming_what_made_you_join_us_today_'].split()))
        # multiple choice
        activity_is.append(
            list(x for x in item['activity_is_a_system_for_'].split()))
    """
    meaning: all_or_complet,peaceful,global,i_give_up
    join: activity_is_a_myst, i_like_beer,to_meet_the_team,not_sure_what_
    activity_is: adaptive_manag an_indicator_t 
        a_data_managem option_4 all_of_the_abo
    """
    meaningcount = dict()
    meaningcount['peaceful'] = 0
    meaningcount['is_global'] = 0
    meaningcount['i_give_up'] = 0
    meaningcount['all_or_complete'] = 0
    for answer in meaning:
        if answer == "all_or_complet":
            meaningcount['all_or_complete'] = meaningcount[
                                                  'all_or_complete'] + 1
        if answer == "global":
            meaningcount['is_global'] = meaningcount['is_global'] + 1
        if answer == "i_give_up":
            meaningcount['i_give_up'] = meaningcount['i_give_up'] + 1
        if answer == "peaceful":
            meaningcount['peaceful'] = meaningcount['peaceful'] + 1

    joincount = dict()
    joincount['activity_is_a_mystery'] = 0
    joincount['i_like_beer'] = 0
    joincount['to_meet_the_team'] = 0
    joincount['not_sure'] = 0
    for answer in join:
        if "activity_is_a_myst" in answer:
            joincount['activity_is_a_mystery'] = \
                joincount['activity_is_a_mystery'] + 1
        if "i_like_beer" in answer:
            joincount['i_like_beer'] = joincount['i_like_beer'] + 1
        if "to_meet_the_team" in answer:
            joincount['to_meet_the_team'] = joincount['to_meet_the_team'] + 1
        if "not_sure_what_" in answer:
            joincount['not_sure'] = joincount['not_sure'] + 1

    activitycount = dict()
    activitycount['adaptive_manag'] = 0
    activitycount['an_indicator_t'] = 0
    activitycount['a_data_managem'] = 0
    activitycount['option_4'] = 0
    activitycount['all_of_the_abo'] = 0
    for answer in activity_is:
        if "adaptive_manag" in answer:
            activitycount['adaptive_manag'] = activitycount[
                                                  'adaptive_manag'] + 1
        if "an_indicator_t" in answer:
            activitycount['an_indicator_t'] = activitycount[
                                                  'an_indicator_t'] + 1
        if "a_data_managem" in answer:
            activitycount['a_data_managem'] = activitycount[
                                                  'a_data_managem'] + 1
        if "option_4" in answer:
            activitycount['option_4'] = activitycount['option_4'] + 1
        if "all_of_the_abo" in answer:
            activitycount['all_of_the_abo'] = activitycount[
                                                  'all_of_the_abo'] + 1

    dashboard = True

    return render(request,
                  "customdashboard/themes/survey_public_dashboard.html",
                  {'meaning': meaningcount, 'join': joincount,
                   'activity_is': activitycount,
                   'countries': countries, 'dashboard': dashboard})


def survey_talk_public_dashboard(request, id=0):
    """
    DEMO only survey for use with public talks about Activity
    Share URL to survey and data will be aggregated in activitytables
    then imported to this dashboard
    :return:
    """
    # get all countires
    countries = Country.objects.all()

    # TODO : change this url
    filter_url = "http://tables.Hikaya.io/api/silo/9/data/"

    headers = {
        'content-type': 'application/json',
        'Authorization': 'Token bd43de0c16ac0400bc404c6598a6fe0e4ce73aa2'}

    response = requests.get(filter_url, headers=headers, verify=False)
    get_json = json.loads(json.dumps(response.content))
    data = ast.literal_eval(get_json)
    meaning = list()
    join = list()
    activity_is = list()
    country_from = list()
    for item in data['data']:
        meaning.append(item['activity_is_a_pashto_word_meaning_'])
        # multiple choice
        join.append(
            list(x for x in item[
                'thanks_for_coming_what_made_you_join_us_today_'].split()))
        # multiple choice
        activity_is.append(
            list(x for x in item['activity_is_a_system_for_'].split()))
        # country
        country_from.append(item['what_country_were_you_in_last'])
    """
    meaning: all_or_complet,peaceful,global,i_give_up
    join: activity_is_a_myst, i_like_a_good_power_point,data_is_king,
        not_sure_what_
    activity_is: adaptive_manag an_indicator_t a_data_managem option_4 
        all_of_the_abo
    """
    meaningcount = dict()
    meaningcount['peaceful'] = 0
    meaningcount['is_global'] = 0
    meaningcount['i_give_up'] = 0
    meaningcount['all_or_complete'] = 0
    for answer in meaning:
        if answer == "all_or_complet":
            meaningcount['all_or_complete'] = meaningcount[
                                                  'all_or_complete'] + 1
        if answer == "global":
            meaningcount['is_global'] = meaningcount['is_global'] + 1
        if answer == "i_give_up":
            meaningcount['i_give_up'] = meaningcount['i_give_up'] + 1
        if answer == "peaceful":
            meaningcount['peaceful'] = meaningcount['peaceful'] + 1

    joincount = dict()
    joincount['activity_is_a_mystery'] = 0
    joincount['i_like_power_point_templates'] = 0
    joincount['data_is_king'] = 0
    joincount['not_sure'] = 0
    for answer in join:
        if "activity_is_a_mystery" in answer:
            joincount['activity_is_a_mystery'] = \
                joincount['activity_is_a_mystery'] + 1
        if "i_like_power_point_templates" in answer:
            joincount['i_like_power_point_templates'] = \
                joincount['i_like_power_point_templates'] + 1
        if "data_is_king" in answer:
            joincount['data_is_king'] = joincount['data_is_king'] + 1
        if "not_sure_what_" in answer:
            joincount['not_sure'] = joincount['not_sure'] + 1

    activitycount = dict()
    activitycount['adaptive_manag'] = 0
    activitycount['an_indicator_t'] = 0
    activitycount['a_data_managem'] = 0
    activitycount['option_4'] = 0
    activitycount['all_of_the_abo'] = 0
    for answer in activity_is:
        if "adaptive_manag" in answer:
            activitycount['adaptive_manag'] = activitycount[
                                                  'adaptive_manag'] + 1
        if "an_indicator_t" in answer:
            activitycount['an_indicator_t'] = activitycount[
                                                  'an_indicator_t'] + 1
        if "a_data_managem" in answer:
            activitycount['a_data_managem'] = activitycount[
                                                  'a_data_managem'] + 1
        if "option_4" in answer:
            activitycount['option_4'] = activitycount['option_4'] + 1
        if "all_of_the_abo" in answer:
            activitycount['all_of_the_abo'] = activitycount[
                                                  'all_of_the_abo'] + 1

    dashboard = True

    return render(request, "customdashboard/survey_talk_public_dashboard.html",
                  {'meaning': meaningcount, 'join': joincount,
                   'activity_is': activitycount,
                   'country_from': country_from, 'countries': countries,
                   'dashboard': dashboard})


# RRIMA PROJECT DASHBOARD (in use 12/16)
def rrima_public_dashboard(request, id=0):
    """
    :param request:
    :param id:
    :return:
    """
    # retrieve program
    model = Program
    program_id = id
    get_program = Program.objects.all().filter(id=program_id)

    # retrieve the coutries the user has data access for
    countries = get_country(request.user)

    # retrieve projects for a program
    # .filter(program__id=1, program__country__in=1)
    get_projects = ProjectAgreement.objects.all()

    page_text = dict()
    page_text['page_title'] = "Refugee Response and Migration News"
    page_text['project_summary'] = {}
    # TODO : Change this variable 
    page_map = [
        {"latitude": 39.9334, "longitude": 32.8597, "location_name": "Ankara",
         "site_contact": "Sonal Shinde, Migration Response Director, "
                         "sshinde@mercycorps.org",
         "site_description": "Migration Response Coordination",
         "region_name": "Turkey"},
        {"latitude": 38.4237, "longitude": 27.1428, "location_name": "Izmir",
         "site_contact": "Tracy Lucas, Emergency Program Manager, ECHO Aegean "
                         "Response, tlucas@mercycorps.org",
         "site_description": "Cash, Information Dissemination, "
                             "Youth, Protection",
         "region_name": "Turkey"},
        {"latitude": 37.0660, "longitude": 37.3781,
         "location_name": "Gaziantep",
         "site_contact": "Jihane Nami, Director of Programs Turkey, "
                         "jnami@mercycorps.org",
         "site_description": "Cash, NFI, Shelter, Protection,"
                             " Information Dissemination",
         "region_name": "Turkey"},
        {"latitude": 39.2645, "longitude": 26.2777, "location_name": "Lesvos",
         "site_contact": "Chiara Bogoni, Island Emergency Program Manager, "
                         "cbogoni@mercycorps.org",
         "site_description": "Cash, Youth Programs, Food",
         "region_link": "Greece"},
        {"latitude": 37.9838, "longitude": 23.7275, "location_name": "Athens",
         "site_contact": "Josh Kreger, Team Leader - Greece, "
                         "jkreger@mercycorps.org and Kaja Wislinska, " +
                         "Team Leader - Athens and Mainland, "
                         "kwislinska@mercycorps.org",
         "site_description": "Cash, Youth Psychosocial Support, Legal Support",
         "region_link": "Greece"},
        {"latitude": 44.7866, "longitude": 20.4489,
         "location_name": "Belgrade",
         "site_contact": "",
         "site_description": "RRIMA (In partnership with IRC) ",
         "region_name": "Balkans"}]
    # Borrowed data for bar graph
    color_palettes = {
        'bright': ['#82BC00', '#C8C500', '#10A400', '#CF102E', '#DB5E11',
                   '#A40D7A', '#00AFA8', '#1349BB', '#FFD200 ',
                   '#FF7100', '#FFFD00', '#ABABAB', '#7F7F7F', '#7B5213',
                   '#C18A34'],
        'light': ['#BAEE46', '#FDFB4A', '#4BCF3D', '#F2637A', '#FFA268',
                  '#C451A4', '#4BC3BE', '#5B7FCC', '#9F54CC',
                  '#FFE464', '#FFA964', '#FFFE64', '#D7D7D7', '#7F7F7F',
                  '#D2A868', '#FFD592']
    }

    get_notebooks = JupyterNotebooks.objects.all().filter(
        very_custom_dashboard="RRIMA")

    return render(request, 'customdashboard/rrima_dashboard.html',
                  {'page_text': page_text, 'page_map': page_map,
                   'countries': countries, 'get_notebooks': get_notebooks})


# RRIMA Custom Dashboard Report Page (in use 12/16)


def notebook(request, id=0):
    """
    :param request:
    :param id:
    :return:
    """
    get_notebook = JupyterNotebooks.objects.get(id=id)
    return render(request, "customdashboard/notebook.html",
                  {'get_notebook': get_notebook})


# RRIMA JupyterView (in use 12/16)


def rrima_jupyter_view1(request, id=0):
    """
    TODO: Migrate this to the existing configurable dashboard
    RRIMA custom dashboard
    :param request:
    :param id:
    :return:
    """
    model = Program
    program_id = 1  # id ##USE TURKEY PROGRAM ID HERE
    # get_program = Program.objects.all().filter(id=program_id)

    # retrieve the coutries the user has data access for
    countries = get_country(request.user)
    with open('static/rrima.html') as myfile:
        data = "\n".join(line for line in myfile)

    return HttpResponse(data)
