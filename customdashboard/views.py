from django.views.generic.list import ListView
from django.http import HttpResponse

from django.shortcuts import render
from workflow.models import ProjectAgreement, ProjectComplete, Program, SiteProfile,Country, TolaSites
from customdashboard.models import ProgramNarratives, JupyterNotebooks
from formlibrary.models import TrainingAttendance, Distribution, Beneficiary
from indicators.models import CollectedData, Indicator, TolaTable

from django.db.models import Sum
from django.db.models import Q

from tola.util import getCountry, get_table

from django.contrib.auth.decorators import login_required
import requests
import json
from datetime import *
import ast

class ProgramList(ListView):
    """
    List of Programs with links to the dashboards
    http://127.0.0.1:8000/customdashboard/program_list/0/
    """
    model = Program
    template_name = 'customdashboard/program_list.html'

    def get(self, request, *args, **kwargs):

        ## retrieve the coutries the user has data access for
        country = None
        countries = getCountry(request.user)
        country_list = Country.objects.all().filter(id__in=countries)
        if int(self.kwargs['pk']) == 0:
            getProgram = Program.objects.all().filter(country__in=countries)
        else:
            getProgram = Program.objects.all().filter(country__id=self.kwargs['pk'])
            country = Country.objects.get(id=self.kwargs['pk']).country

        program_list = []
        for program in getProgram:
            # get the percentage of indicators with data
            getInidcatorDataCount = Indicator.objects.filter(program__id=program.id).exclude(collecteddata__periodic_target=None).count()
            getInidcatorCount = Indicator.objects.filter(program__id=program.id).count()
            if getInidcatorCount > 0 and getInidcatorDataCount > 0:
                getInidcatorDataPercent = 100 * float(getInidcatorDataCount) / float(getInidcatorCount)
            else:
                getInidcatorDataPercent = 0

            program.indicator_data_percent = int(getInidcatorDataPercent)
            program.indicator_percent = int(100 - getInidcatorDataPercent)

            # get the percentage of projects with completes (tracking)
            getProjectAgreementCount = ProjectAgreement.objects.filter(program__id=program.id).count()
            getProjectCompleteCount = ProjectComplete.objects.filter(program__id=program.id).count()
            if getProjectAgreementCount > 0 and getProjectCompleteCount > 0:
                project_percent = 100 * float(getProjectCompleteCount) / float(getProjectAgreementCount)
            else:
                project_percent = 0

            # append the rounded percentages to the program list
            program.project_percent = int(project_percent)
            program.project_agreement_percent = int(100 - project_percent)
            program_list.append(program)

        return render(request, self.template_name, {'getProgram': program_list, 'getCountry': country_list, 'country': country})


@login_required(login_url='/accounts/login/')
def DefaultCustomDashboard(request,id=0,status=0):
    """
    This is used as the workflow program dashboard
    # of agreements, approved, rejected, waiting, archived and total for dashboard
    http://127.0.0.1:8000/customdashboard/65/
    """
    program_id = id

    countries = getCountry(request.user)

    #transform to list if a submitted country
    selected_countries_list = Country.objects.all().filter(program__id=program_id)

    getQuantitativeDataSums = CollectedData.objects.filter(indicator__program__id=program_id,achieved__isnull=False, indicator__key_performance_indicator=True).exclude(achieved=None).order_by('indicator__number').values('indicator__number','indicator__name','indicator__id').annotate(targets=Sum('periodic_target__target'), actuals=Sum('achieved')).exclude(achieved=None)

    totalTargets = getQuantitativeDataSums.aggregate(Sum('targets'))
    totalActuals = getQuantitativeDataSums.aggregate(Sum('actuals'))

    getFilteredName=Program.objects.get(id=program_id)

    getProjectsCount = ProjectAgreement.objects.all().filter(program__id=program_id, program__country__in=countries).count()
    getBudgetEstimated = ProjectAgreement.objects.all().filter(program__id=program_id, program__country__in=countries).annotate(estimated=Sum('total_estimated_budget'))
    getAwaitingApprovalCount = ProjectAgreement.objects.all().filter(program__id=program_id, approval='awaiting approval', program__country__in=countries).count()
    getApprovedCount = ProjectAgreement.objects.all().filter(program__id=program_id, approval='approved', program__country__in=countries).count()
    getRejectedCount = ProjectAgreement.objects.all().filter(program__id=program_id, approval='rejected', program__country__in=countries).count()
    getInProgressCount = ProjectAgreement.objects.all().filter(program__id=program_id).filter(Q(Q(approval='in progress') | Q(approval=None)), program__country__in=countries).count()
    nostatus_count = ProjectAgreement.objects.all().filter(program__id=program_id).filter(Q(Q(approval=None) | Q(approval=""))).count()

    getSiteProfile = SiteProfile.objects.all().filter(Q(projectagreement__program__id=program_id) | Q(collecteddata__program__id=program_id))
    getSiteProfileIndicator = SiteProfile.objects.all().filter(Q(collecteddata__program__id=program_id))

    if (status) =='Approved':
       getProjects = ProjectAgreement.objects.all().filter(program__id=program_id, program__country__in=countries, approval='approved').prefetch_related('projectcomplete')
    elif(status) =='Rejected':
       getProjects = ProjectAgreement.objects.all().filter(program__id=program_id, program__country__in=countries, approval='rejected').prefetch_related('projectcomplete')
    elif(status) =='In Progress':
       getProjects = ProjectAgreement.objects.all().filter(program__id=program_id, program__country__in=countries, approval='in progress').prefetch_related('projectcomplete')
    elif(status) =='Awaiting Approval':
       getProjects = ProjectAgreement.objects.all().filter(program__id=program_id, program__country__in=countries, approval='awaiting approval').prefetch_related('projectcomplete')
    else:
       getProjects = ProjectAgreement.objects.all().filter(program__id=program_id, program__country__in=countries)

    get_project_completed = []

    totalBudgetted = 0.00
    totalActual = 0.00

    getProjectsComplete = ProjectComplete.objects.all()
    for project in getProjects:
        for complete in getProjectsComplete:
            if complete.actual_budget != None:
                if project.id == complete.project_agreement_id:
                    totalBudgetted = float(totalBudgetted) + float(project.total_estimated_budget)
                    totalActual = float(totalActual) + float(complete.actual_budget)

                    get_project_completed.append(project)

    return render(request, "customdashboard/customdashboard/visual_dashboard.html", {'getSiteProfile':getSiteProfile, 'getBudgetEstimated': getBudgetEstimated, 'getQuantitativeDataSums': getQuantitativeDataSums,
                                                                     'country': countries, 'getAwaitingApprovalCount':getAwaitingApprovalCount,
                                                                     'getFilteredName': getFilteredName,'getProjects': getProjects, 'getApprovedCount': getApprovedCount,
                                                                     'getRejectedCount': getRejectedCount, 'getInProgressCount': getInProgressCount,'nostatus_count': nostatus_count,
                                                                     'getProjectsCount': getProjectsCount, 'selected_countries_list': selected_countries_list,
                                                                     'getSiteProfileIndicator': getSiteProfileIndicator, 'get_project_completed': get_project_completed, 'totalActuals': totalActuals, 'totalTargets': totalTargets, 'totalBudgetted': totalBudgetted, 'totalActual': totalActual})


def PublicDashboard(request,id=0,public=0):
    """
    This is used as the internal and external (public) dashboard view
    the template is changed for public
    :public: if URL contains a 0 then show the internal dashboard
    if 1 then public dashboard
    http://127.0.0.1:8000/customdashboard/program_dashboard/65/0/
    """
    program_id = id
    getQuantitativeDataSums_2 = CollectedData.objects.all().filter(indicator__program__id=program_id,achieved__isnull=False).order_by('indicator__source').values('indicator__number','indicator__source','indicator__id')
    getQuantitativeDataSums = CollectedData.objects.filter(indicator__program__id=program_id,achieved__isnull=False).exclude(achieved=None).order_by('indicator__number').values('indicator__number','indicator__name','indicator__id').annotate(targets=Sum('periodic_target__target'), actuals=Sum('achieved'))
    getIndicatorCount = Indicator.objects.all().filter(program__id=program_id).count()

    getIndicatorData = CollectedData.objects.all().filter(indicator__program__id=program_id,achieved__isnull=False).order_by('date_collected')

    getIndicatorCountData = getIndicatorData.count()

    getIndicatorCountKPI = Indicator.objects.all().filter(program__id=program_id,key_performance_indicator=1).count()
    getProgram = Program.objects.all().get(id=program_id)
    try:
        getProgramNarrative = ProgramNarratives.objects.get(program_id=program_id)
    except ProgramNarratives.DoesNotExist:
        getProgramNarrative = None
    getProjects = ProjectComplete.objects.all().filter(program_id=program_id)
    getAllProjects = ProjectAgreement.objects.all().filter(program_id=program_id)
    getSiteProfile = SiteProfile.objects.all().filter(projectagreement__program__id=program_id)
    getSiteProfileIndicator = SiteProfile.objects.all().filter(Q(collecteddata__program__id=program_id))

    getProjectsCount = ProjectAgreement.objects.all().filter(program__id=program_id).count()
    getAwaitingApprovalCount = ProjectAgreement.objects.all().filter(program__id=program_id, approval='awaiting approval').count()
    getApprovedCount = ProjectAgreement.objects.all().filter(program__id=program_id, approval='approved').count()
    getRejectedCount = ProjectAgreement.objects.all().filter(program__id=program_id, approval='rejected').count()
    getInProgressCount = ProjectAgreement.objects.all().filter(Q(program__id=program_id) & Q(Q(approval='in progress') | Q(approval=None) | Q(approval=""))).count()

    nostatus_count = ProjectAgreement.objects.all().filter(Q(program__id=program_id) & Q(Q(approval=None) | Q(approval=""))).count()

    getNotebooks = JupyterNotebooks.objects.all().filter(program__id=program_id)

    # get all countires
    countries = Country.objects.all().filter(program__id=program_id)

    # Trainings
    agreement_id_list = []
    training_id_list = []

    # Indicator Evidence
    getEvidence = TolaTable.objects.all().filter(country__in=countries)
    evidence_tables_count = getEvidence.count()
    evidence_tables = []

    try:
        for table in getEvidence:

            table.table_data = get_table(table.url)

            print table.table_data

            evidence_tables.append(table)

    except Exception, e:
        pass

    for p in getProjects:
        agreement_id_list.append(p.id)

    getTrainings = TrainingAttendance.objects.all().filter(project_agreement_id__in=agreement_id_list)

    getDistributions = Distribution.objects.all().filter(initiation_id__in=agreement_id_list)

    for t in getTrainings:
        training_id_list.append(t.id)

    getBeneficiaries = Beneficiary.objects.all().filter(training__in=training_id_list)

    get_project_completed = []

    getProjectsComplete = ProjectComplete.objects.all()
    for project in getProjects:
        for complete in getProjectsComplete:
            if complete.actual_budget != None:
                if project.id == complete.project_agreement_id:
                    get_project_completed.append(project)

    # public dashboards have a different template display
    if int(public) == 1:
        print "public"
        template = "customdashboard/publicdashboard/public_dashboard.html"
    else:
        template = "customdashboard/publicdashboard/program_dashboard.html"

    return render(request, template, {'getProgram':getProgram,'getProjects':getProjects,
                                                                     'getSiteProfile':getSiteProfile,
                                                                     'countries': countries, 'getProgramNarrative': getProgramNarrative,
                                                                     'getAwaitingApprovalCount':getAwaitingApprovalCount,'getQuantitativeDataSums_2':getQuantitativeDataSums_2,
                                                                     'getApprovedCount': getApprovedCount,
                                                                     'getRejectedCount': getRejectedCount,
                                                                     'getInProgressCount': getInProgressCount,'nostatus_count': nostatus_count,
                                                                     'total_projects': getProjectsCount,
                                                                     'getIndicatorCount': getIndicatorCount,
                                                                     'getIndicatorData': getIndicatorData,
                                                                     'getIndicatorCountData':getIndicatorCountData,
                                                                     'getIndicatorCountKPI': getIndicatorCountKPI,
                                                                     'getEvidence': getEvidence,
                                                                     'evidence_tables': evidence_tables,
                                                                     'getNotebooks': getNotebooks,
                                                                     'evidence_tables_count': evidence_tables_count,
                                                                     'getQuantitativeDataSums': getQuantitativeDataSums,
                                                                     'getSiteProfileIndicator': getSiteProfileIndicator, 'getSiteProfileIndicatorCount': getSiteProfileIndicator.count(), 'getBeneficiaries': getBeneficiaries, 'getDistributions': getDistributions, 'getTrainings': getTrainings, 'get_project_completed': get_project_completed, 'getAllProjects': getAllProjects})


"""
Extremely Customized dashboards
This section contains custom dashboards or one-off dashboard for demo, or specific
customer requests outside the scope of customized program dashboards
"""
def SurveyPublicDashboard(request,id=0):
    """
    DEMO only survey for Tola survey
    :return:
    """

    # get all countires
    countries = Country.objects.all()

    filter_url = "http://tola-tables.mercycorps.org/api/silo/430/data/"
    token = TolaSites.objects.get(site_id=1)
    if token.tola_tables_token:
        headers = {'content-type': 'application/json',
                   'Authorization': 'Token ' + token.tola_tables_token}
    else:
        headers = {'content-type': 'application/json'}
        print "Token Not Found"

    response = requests.get(filter_url, headers=headers, verify=False)
    get_json = json.loads(response.content)
    data = ast.literal_eval(get_json)
    meaning = []
    join = []
    tola_is = []
    for item in data['data']:
        print item['tola_is_a_pashto_word_meaning_']
        meaning.append(item['tola_is_a_pashto_word_meaning_'])
        # multiple choice
        join.append(list(x for x in item['thanks_for_coming_what_made_you_join_us_today_'].split()))
        # multiple choice
        tola_is.append(list(x for x in item['tola_is_a_system_for_'].split()))
    """
    meaning: all_or_complet,peaceful,global,i_give_up
    join: tola_is_a_myst, i_like_beer,to_meet_the_team,not_sure_what_
    tola_is: adaptive_manag an_indicator_t a_data_managem option_4 all_of_the_abo
    """
    meaningcount = {}
    meaningcount['peaceful'] = 0
    meaningcount['is_global'] = 0
    meaningcount['i_give_up'] = 0
    meaningcount['all_or_complete'] = 0
    for answer in meaning:
        if answer == "all_or_complet":
            meaningcount['all_or_complete'] = meaningcount['all_or_complete'] + 1
        if answer == "global":
            meaningcount['is_global'] = meaningcount['is_global'] + 1
        if answer == "i_give_up":
            meaningcount['i_give_up'] = meaningcount['i_give_up'] + 1
        if answer == "peaceful":
            meaningcount['peaceful'] = meaningcount['peaceful'] + 1

    joincount = {}
    joincount['tola_is_a_mystery'] = 0
    joincount['i_like_beer'] = 0
    joincount['to_meet_the_team'] = 0
    joincount['not_sure'] = 0
    for answer in join:
        if "tola_is_a_myst" in answer:
            joincount['tola_is_a_mystery'] = joincount['tola_is_a_mystery'] + 1
        if "i_like_beer" in answer:
            joincount['i_like_beer'] = joincount['i_like_beer'] + 1
        if "to_meet_the_team" in answer:
            joincount['to_meet_the_team'] = joincount['to_meet_the_team'] + 1
        if "not_sure_what_" in answer:
            joincount['not_sure'] = joincount['not_sure'] + 1

    tolacount = {}
    tolacount['adaptive_manag'] = 0
    tolacount['an_indicator_t'] = 0
    tolacount['a_data_managem'] = 0
    tolacount['option_4'] = 0
    tolacount['all_of_the_abo'] = 0
    for answer in tola_is:
        if "adaptive_manag" in answer:
            tolacount['adaptive_manag'] = tolacount['adaptive_manag'] + 1
        if "an_indicator_t" in answer:
            tolacount['an_indicator_t'] = tolacount['an_indicator_t'] + 1
        if "a_data_managem" in answer:
            tolacount['a_data_managem'] = tolacount['a_data_managem'] + 1
        if "option_4" in answer:
            tolacount['option_4'] = tolacount['option_4'] + 1
        if "all_of_the_abo" in answer:
            tolacount['all_of_the_abo'] = tolacount['all_of_the_abo'] + 1

    dashboard = True

    return render(request, "customdashboard/themes/survey_public_dashboard.html", {'meaning':meaningcount,'join':joincount,'tola_is':tolacount, 'countries': countries, 'dashboard':dashboard})


def SurveyTalkPublicDashboard(request,id=0):
    """
    DEMO only survey for Tola survey for use with public talks about TolaData
    Share URL to survey and data will be aggregated in tolatables
    then imported to this dashboard
    :return:
    """
    # get all countires
    countries = Country.objects.all()

    filter_url = "http://tables.toladata.io/api/silo/9/data/"

    headers = {'content-type': 'application/json',
               'Authorization': 'Token bd43de0c16ac0400bc404c6598a6fe0e4ce73aa2'}

    response = requests.get(filter_url, headers=headers, verify=False)
    get_json = json.loads(json.dumps(response.content))
    data = ast.literal_eval(get_json)
    meaning = []
    join = []
    tola_is = []
    country_from = []
    for item in data['data']:
        meaning.append(item['tola_is_a_pashto_word_meaning_'])
        # multiple choice
        join.append(list(x for x in item['thanks_for_coming_what_made_you_join_us_today_'].split()))
        # multiple choice
        tola_is.append(list(x for x in item['tola_is_a_system_for_'].split()))
        # country
        country_from.append(item['what_country_were_you_in_last'])
    """
    meaning: all_or_complet,peaceful,global,i_give_up
    join: tola_is_a_myst, i_like_a_good_power_point,data_is_king,not_sure_what_
    tola_is: adaptive_manag an_indicator_t a_data_managem option_4 all_of_the_abo
    """
    meaningcount = {}
    meaningcount['peaceful'] = 0
    meaningcount['is_global'] = 0
    meaningcount['i_give_up'] = 0
    meaningcount['all_or_complete'] = 0
    for answer in meaning:
        if answer == "all_or_complet":
            meaningcount['all_or_complete'] = meaningcount['all_or_complete'] + 1
        if answer == "global":
            meaningcount['is_global'] = meaningcount['is_global'] + 1
        if answer == "i_give_up":
            meaningcount['i_give_up'] = meaningcount['i_give_up'] + 1
        if answer == "peaceful":
            meaningcount['peaceful'] = meaningcount['peaceful'] + 1

    joincount = {}
    joincount['tola_is_a_mystery'] = 0
    joincount['i_like_power_point_templates'] = 0
    joincount['data_is_king'] = 0
    joincount['not_sure'] = 0
    for answer in join:
        if "tola_is_a_mystery" in answer:
            joincount['tola_is_a_mystery'] = joincount['tola_is_a_mystery'] + 1
        if "i_like_power_point_templates" in answer:
            joincount['i_like_power_point_templates'] = joincount['i_like_power_point_templates'] + 1
        if "data_is_king" in answer:
            joincount['data_is_king'] = joincount['data_is_king'] + 1
        if "not_sure_what_" in answer:
            joincount['not_sure'] = joincount['not_sure'] + 1

    tolacount = {}
    tolacount['adaptive_manag'] = 0
    tolacount['an_indicator_t'] = 0
    tolacount['a_data_managem'] = 0
    tolacount['option_4'] = 0
    tolacount['all_of_the_abo'] = 0
    for answer in tola_is:
        if "adaptive_manag" in answer:
            tolacount['adaptive_manag'] = tolacount['adaptive_manag'] + 1
        if "an_indicator_t" in answer:
            tolacount['an_indicator_t'] = tolacount['an_indicator_t'] + 1
        if "a_data_managem" in answer:
            tolacount['a_data_managem'] = tolacount['a_data_managem'] + 1
        if "option_4" in answer:
            tolacount['option_4'] = tolacount['option_4'] + 1
        if "all_of_the_abo" in answer:
            tolacount['all_of_the_abo'] = tolacount['all_of_the_abo'] + 1

    dashboard = True

    return render(request, "customdashboard/survey_talk_public_dashboard.html", {'meaning':meaningcount,'join':joincount,'tola_is':tolacount, 'country_from': country_from, 'countries': countries, 'dashboard':dashboard})



#RRIMA PROJECT DASHBOARD (in use 12/16)
def RRIMAPublicDashboard(request,id=0):
    """
    :param request:
    :param id:
    :return:
    """
    ## retrieve program
    model = Program
    program_id = id
    getProgram = Program.objects.all().filter(id=program_id)


    ## retrieve the coutries the user has data access for
    countries = getCountry(request.user)

    #retrieve projects for a program
    getProjects = ProjectAgreement.objects.all()##.filter(program__id=1, program__country__in=1)

    pageText = {}
    pageText['pageTitle'] = "Refugee Response and Migration News"
    pageText['projectSummary'] = {}

    pageMap = [{"latitude":39.9334, "longitude":32.8597, "location_name":"Ankara","site_contact":"Sonal Shinde, Migration Response Director, sshinde@mercycorps.org", "site_description":"Migration Response Coordination","region_name":"Turkey"},
        {"latitude":38.4237, "longitude":27.1428, "location_name":"Izmir","site_contact":"Tracy Lucas, Emergency Program Manager, ECHO Aegean Response, tlucas@mercycorps.org", "site_description":"Cash, Information Dissemination, Youth, Protection", "region_name":"Turkey"},
        {"latitude":37.0660, "longitude":37.3781, "location_name":"Gaziantep","site_contact":"Jihane Nami, Director of Programs Turkey, jnami@mercycorps.org", "site_description":"Cash, NFI, Shelter, Protection, Information Dissemination","region_name":"Turkey"},
        {"latitude":39.2645, "longitude":26.2777, "location_name":"Lesvos", "site_contact":"Chiara Bogoni, Island Emergency Program Manager, cbogoni@mercycorps.org", "site_description":"Cash, Youth Programs, Food","region_link":"Greece"},
        {"latitude":37.9838, "longitude":23.7275, "location_name":"Athens", "site_contact":"Josh Kreger, Team Leader - Greece, jkreger@mercycorps.org and Kaja Wislinska, Team Leader - Athens and Mainland, kwislinska@mercycorps.org","site_description":"Cash, Youth Psychosocial Support, Legal Support","region_link":"Greece","region_link":"Greece"},
        {"latitude":44.7866, "longitude":20.4489, "location_name":"Belgrade","site_contact":"","site_description":"RRIMA (In partnership with IRC) ","region_name":"Balkans"}]
   # Borrowed data for bar graph
    colorPalettes = {
    'bright':['#82BC00','#C8C500','#10A400','#CF102E','#DB5E11','#A40D7A','#00AFA8','#1349BB','#FFD200 ','#FF7100','#FFFD00','#ABABAB','#7F7F7F','#7B5213','#C18A34'],
    'light':['#BAEE46','#FDFB4A','#4BCF3D','#F2637A','#FFA268','#C451A4','#4BC3BE','#5B7FCC','#9F54CC','#FFE464','#FFA964','#FFFE64','#D7D7D7','#7F7F7F','#D2A868','#FFD592']
    };

    getNotebooks = JupyterNotebooks.objects.all().filter(very_custom_dashboard="RRIMA")

    return render(request, 'customdashboard/rrima_dashboard.html',
        {'pageText': pageText, 'pageMap': pageMap, 'countries': countries, 'getNotebooks':getNotebooks})

#RRIMA Custom Dashboard Report Page (in use 12/16)
def Notebook(request,id=0):
    """
    :param request:
    :param id:
    :return:
    """
    getNotebook = JupyterNotebooks.objects.get(id=id)
    return render(request, "customdashboard/notebook.html", {'getNotebook':getNotebook})

#RRIMA JupyterView (in use 12/16)
def RRIMAJupyterView1(request,id=0):
    """
    RRIMA custom dashboard TODO: Migrate this to the existing configurable dashboard
    :param request:
    :param id:
    :return:
    """
    model = Program
    program_id = 1#id ##USE TURKEY PROGRAM ID HERE
    # getProgram = Program.objects.all().filter(id=program_id)

    ## retrieve the coutries the user has data access for
    countries = getCountry(request.user)
    with open('static/rrima.html') as myfile: data = "\n".join(line for line in myfile)

    return HttpResponse(data)