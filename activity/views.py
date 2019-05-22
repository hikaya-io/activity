#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Q, Count

from indicators.models import CollectedData, Indicator

from workflow.models import (
    ProjectAgreement, ProjectComplete, Program,
    SiteProfile, Sector, Country, ActivityUser,
    ActivitySites, ActivityBookmarks, FormGuidance, Organization
)
from activity.tables import IndicatorDataTable
from activity.util import get_country, get_nav_links
from activity.forms import (
    RegistrationForm, NewUserRegistrationForm,
    NewActivityUserRegistrationForm, BookmarkForm
)


@login_required(login_url='/accounts/login/')
def index(request, selected_countries=None, id=0, sector=0):
    """
    Home page
    get count of agreements approved and total for dashboard
    """

    # add program
    if request.method == 'POST' and request.is_ajax:
        data = request.POST

        program = Program.objects.create(name=data.get(
            'program_name'), start_date=data.get('start_date'), end_date=data.get('end_date'))

        sectors = Sector.objects.filter(id__in=data.getlist('sectors[]'))
        program.sector.set(sectors)

        # Return a "created" (201) response code.
        return HttpResponse(status=201, content_type="application/json")

    program_id = id
    user_countries = get_country(request.user)

    if not selected_countries:
        selected_countries = user_countries
        selected_countries_list = None
        selected_countries_label_list = None
    else:
        # transform to list if a submitted country
        selected_countries = [selected_countries]
        selected_countries_list = Country.objects.all().filter(
            id__in=selected_countries)
        selected_countries_label_list = Country.objects.all().filter(
            id__in=selected_countries).values('country')

    get_agency_site = ActivitySites.objects.all().filter(id=1)
    get_sectors = Sector.objects.all().exclude(
        program__isnull=True).select_related()
    get_all_sectors = Sector.objects.all()

    # limit the programs by the selected sector
    if int(sector) == 0:
        get_programs = Program.objects.all()\
            .prefetch_related('agreement', 'agreement__office').filter(
            funding_status="Funded", country__in=selected_countries)
        # .exclude(agreement__isnull=True)
        sectors = Sector.objects.all()
    else:
        get_programs = Program.objects.all()\
            .filter(funding_status="Funded",
                    country__in=selected_countries, sector=sector)
        sectors = Sector.objects.all().filter(id=sector)

    filter_for_quantitative_data_sums = {
        'indicator__key_performance_indicator': True,
        'periodic_target__isnull': False,
        'achieved__isnull': False,
    }

    # get data for just one program or all programs
    if int(program_id) == 0:
        get_filtered_name = None
        filter_for_quantitative_data_sums[
            'indicator__program__country__in'] = selected_countries

        # filter by all programs then filter by sector if found
        if int(sector) > 0:
            filter_for_quantitative_data_sums[
                'agreement__sector__in'] = sectors
            get_site_profile = SiteProfile.objects.all().prefetch_related(
                'country', 'district', 'province').filter(
                Q(Q(projectagreement__sector__in=sectors)),
                country__in=selected_countries).filter(status=1)
            get_site_profile_indicator = SiteProfile.objects.all()\
                .prefetch_related('country', 'district', 'province').filter(
                Q(collecteddata__program__country__in=selected_countries))\
                .filter(status=1)
            agreement_total_count = ProjectAgreement.objects.all().filter(
                sector__in=sectors,
                program__country__in=selected_countries).count()
            complete_total_count = ProjectComplete.objects.all().filter(
                project_agreement__sector__in=sectors,
                program__country__in=selected_countries).count()
            agreement_approved_count = ProjectAgreement.objects.all().filter(
                approval='approved', sector__in=sectors,
                program__country__in=selected_countries).count()
            complete_approved_count = ProjectComplete.objects.all().filter(
                approval='approved', project_agreement__sector__in=sectors,
                program__country__in=selected_countries).count()

            agreement_awaiting_count = ProjectAgreement.objects.all().filter(
                approval='awaiting approval', sector__in=sectors,
                program__country__in=selected_countries).count()

            complete_awaiting_count = ProjectComplete.objects.all().filter(
                approval='awaiting approval',
                project_agreement__sector__in=sectors,
                program__country__in=selected_countries).count()

            agreement_open_count = ProjectAgreement.objects.all().filter(
                Q(Q(approval='open') | Q(approval="") | Q(
                    approval=None)), sector__id__in=sectors,
                program__country__in=selected_countries).count()
            complete_open_count = ProjectComplete.objects.all().filter(
                Q(Q(approval='open') | Q(approval="") | Q(approval=None)),
                project_agreement__sector__in=sectors,
                program__country__in=selected_countries).count()
            agreement_wait_count = ProjectAgreement.objects.all().filter(
                Q(approval='in progress') & Q(
                    Q(approval='in progress') | Q(approval=None) | Q(
                        approval="")),
                sector__in=sectors,
                program__country__in=selected_countries).count()
            complete_wait_count = ProjectComplete.objects.all().filter(
                Q(approval='in progress') & Q(
                    Q(approval='in progress') | Q(approval=None) | Q(
                        approval="")),
                project_agreement__sector__in=sectors,
                program__country__in=selected_countries).count()

        else:
            get_site_profile = SiteProfile.objects.all().prefetch_related(
                'country', 'district', 'province').filter(
                country__in=selected_countries).filter(status=1)
            get_site_profile_indicator = SiteProfile.objects.all()\
                .prefetch_related('country', 'district', 'province').filter(
                Q(collecteddata__program__country__in=selected_countries))\
                .filter(status=1)
            agreement_total_count = ProjectAgreement.objects.all().filter(
                program__country__in=selected_countries).count()
            complete_total_count = ProjectComplete.objects.all().filter(
                program__country__in=selected_countries).count()
            agreement_approved_count = ProjectAgreement.objects.all().filter(
                approval='approved',
                program__country__in=selected_countries).count()
            complete_approved_count = ProjectComplete.objects.all().filter(
                approval='approved',
                program__country__in=selected_countries).count()

            agreement_awaiting_count = ProjectAgreement.objects.all().filter(
                approval='awaiting approval',
                program__country__in=selected_countries).count()
            complete_awaiting_count = ProjectComplete.objects.all().filter(
                approval='awaiting approval',
                program__country__in=selected_countries).count()
            agreement_open_count = ProjectAgreement.objects.all().filter(
                Q(Q(approval='open') | Q(
                    approval="") | Q(approval=None)),
                program__country__in=selected_countries).count()
            complete_open_count = ProjectComplete.objects.all().filter(
                Q(Q(approval='open') | Q(
                    approval="") | Q(approval=None)),
                program__country__in=selected_countries).count()
            agreement_wait_count = ProjectAgreement.objects.all().filter(
                Q(approval='in progress') & Q(
                    Q(approval='in progress') | Q(approval=None) | Q(
                        approval="")),
                program__country__in=selected_countries).count()
            complete_wait_count = ProjectComplete.objects.all().filter(
                Q(approval='in progress') &
                Q(Q(approval='in progress') |
                  Q(approval=None) | Q(approval="")),
                program__country__in=selected_countries).count()

    else:
        filter_for_quantitative_data_sums[
            'indicator__program__id'] = program_id

        get_filtered_name = Program.objects.get(id=program_id)
        agreement_total_count = ProjectAgreement.objects.all().filter(
            program__id=program_id).count()
        complete_total_count = ProjectComplete.objects.all().filter(
            program__id=program_id).count()
        agreement_approved_count = ProjectAgreement.objects.all().filter(
            program__id=program_id, approval='approved').count()
        complete_approved_count = ProjectComplete.objects.all().filter(
            program__id=program_id, approval='approved').count()
        agreement_open_count = ProjectAgreement.objects.all().filter(
            program__id=program_id, approval='open').count()
        complete_open_count = ProjectComplete.objects.all().filter(
            Q(Q(approval='open') | Q(approval="")),
            program__id=program_id).count()
        agreement_wait_count = ProjectAgreement.objects.all().filter(
            Q(program__id=program_id), Q(
                approval='in progress') & Q(
                Q(approval='in progress') | Q(approval=None) | Q(
                    approval=""))).count()
        complete_wait_count = ProjectComplete.objects.all().filter(
            Q(program__id=program_id), Q(
                approval='in progress') & Q(
                Q(approval='in progress') | Q(approval=None) | Q(
                    approval=""))).count()
        get_site_profile = SiteProfile.objects.all().prefetch_related(
            'country', 'district', 'province').filter(
            projectagreement__program__id=program_id).filter(status=1)
        get_site_profile_indicator = SiteProfile.objects.all()\
            .prefetch_related('country', 'district', 'province').filter(
            Q(collecteddata__program__id=program_id)).filter(status=1)

        agreement_awaiting_count = ProjectAgreement.objects.all().filter(
            program__id=program_id, approval='awaiting approval').count()
        complete_awaiting_count = ProjectComplete.objects.all().filter(
            program__id=program_id, approval='awaiting approval').count()

    get_quantitative_data_sums = CollectedData.objects.all() \
        .filter(**filter_for_quantitative_data_sums) \
        .exclude(achieved=None, periodic_target=None,
                 program__funding_status="Archived") \
        .order_by('indicator__program', 'indicator__number') \
        .values('indicator__lop_target', 'indicator__program__id',
                'indicator__program__name',
                'indicator__number', 'indicator__name', 'indicator__id') \
        .annotate(targets=Sum('periodic_target'), actuals=Sum('achieved'))

    # Evidence and Objectives are for the global leader dashboard
    # items and are the same every time
    count_evidence = CollectedData.objects.all().filter(
        indicator__isnull=False) \
        .values("indicator__program__country__country").annotate(
        evidence_count=Count('evidence', distinct=True) + Count(
            'activity_table', distinct=True),
        indicator_count=Count('pk', distinct=True)).order_by('-evidence_count')
    get_objectives = CollectedData.objects.filter(
        indicator__strategic_objectives__isnull=False,
        indicator__program__country__in=selected_countries) \
        .exclude(
        achieved=None,
        periodic_target=None) \
        .order_by('indicator__strategic_objectives__name') \
        .values('indicator__strategic_objectives__name') \
        .annotate(
        indicators=Count('indicator__pk', distinct=True),
        targets=Sum('periodic_target__target'), actuals=Sum('achieved'))
    table = IndicatorDataTable(get_quantitative_data_sums)
    table.paginate(page=request.GET.get('page', 1), per_page=20)

    count_program = Program.objects.all().filter(
        country__in=selected_countries, funding_status='Funded').count()

    approved_by = ActivityUser.objects.get(user_id=request.user)
    user_pending_approvals = ProjectAgreement.objects.filter(
        approved_by=approved_by).exclude(approval='approved')

    count_program_agreement = ProjectAgreement.objects.all().filter(
        program__country__in=selected_countries,
        program__funding_status='Funded').values('program').distinct().count()
    count_indicator = Indicator.objects.all().filter(
        program__country__in=selected_countries,
        program__funding_status='Funded').values('program').distinct().count()
    count_evidence_adoption = CollectedData.objects.all().filter(
        indicator__isnull=False,
        indicator__program__country__in=selected_countries) \
        .values("indicator__program__country__country") \
        .annotate(evidence_count=Count('evidence', distinct=True) + Count(
            'activity_table', distinct=True),
        indicator_count=Count('pk', distinct=True)).order_by(
        '-evidence_count')
    count_program = int(count_program)
    count_program_agreement = int(count_program_agreement)

    green = "#5CB85C"
    yellow = "#E89424"
    red = "#B30838"

    # 66% or higher = Green above 25% below %66 is Orange and below %25 is Red

    if count_program_agreement >= float(count_program / 1.5):
        workflow_adoption = green
    elif count_program / 1.5 > count_program_agreement > count_program / 4:
        workflow_adoption = yellow
    elif count_program_agreement <= count_program / 4:
        workflow_adoption = red

    if count_indicator >= float(count_program / 1.5):
        indicator_adoption = green
    elif count_program / 1.5 > count_indicator > count_program / 4:
        indicator_adoption = yellow
    elif count_indicator <= count_program / 4:
        indicator_adoption = red

    total_evidence_adoption_count = 0
    total_indicator_data_count = 0
    for country in count_evidence_adoption:
        total_evidence_adoption_count = total_evidence_adoption_count + \
            country['evidence_count']
        total_indicator_data_count = total_indicator_data_count + \
            country['indicator_count']

    if total_evidence_adoption_count >= float(
            total_indicator_data_count / 1.5):
        evidence_adoption = green
    elif total_indicator_data_count / 1.5 > total_evidence_adoption_count > \
            total_indicator_data_count / 4:
        evidence_adoption = yellow
    elif total_evidence_adoption_count <= total_indicator_data_count / 4:
        evidence_adoption = red

    return render(request, "index.html", {
        'agreement_total_count': agreement_total_count,
        'agreement_approved_count': agreement_approved_count,
        'agreement_open_count': agreement_open_count,
        'agreement_wait_count': agreement_wait_count,
        'agreement_awaiting_count': agreement_awaiting_count,
        'complete_open_count': complete_open_count,
        'complete_approved_count': complete_approved_count,
        'complete_total_count': complete_total_count,
        'complete_wait_count': complete_wait_count,
        'complete_awaiting_count': complete_awaiting_count,
        'programs': get_programs,
        'getSiteProfile': get_site_profile,
        'countries': user_countries,
        'selected_countries': selected_countries,
        'getFilteredName': get_filtered_name,
        'getSectors': get_sectors,
        'get_all_sectors': get_all_sectors,
        'sector': sector, 'table': table,
        'getQuantitativeDataSums': get_quantitative_data_sums,
        'count_evidence': count_evidence,
        'getObjectives': get_objectives,
        'selected_countries_list': selected_countries_list,
        'getSiteProfileIndicator': get_site_profile_indicator,
        'getAgencySite': get_agency_site,
        'workflow_adoption': workflow_adoption,
        'count_program': count_program,
        'count_program_agreement': count_program_agreement,
        'indicator_adoption': indicator_adoption,
        'count_indicator': count_indicator,
        'evidence_adoption': evidence_adoption,
        'count_evidence_adoption': total_evidence_adoption_count,
        'count_indicator_data': total_indicator_data_count,
        'selected_countries_label_list': selected_countries_label_list,
        'user_pending_approvals': user_pending_approvals,
    })


def register(request):
    """
    Register a new User profile using built in Django Users Model
    """
    privacy = ActivitySites.objects.get(id=1)
    if request.method == 'POST':
        uf = NewUserRegistrationForm(request.POST)
        tf = NewActivityUserRegistrationForm(request.POST)

        if uf.is_valid() * tf.is_valid():
            user = uf.save()
            user.groups.add(Group.objects.get(name='ViewOnly'))

            activityuser = tf.save(commit=False)
            activityuser.user = user
            activityuser.save()
            messages.error(
                request, 'Thank you, You have been registered as a new user.',
                fail_silently=False)
            return HttpResponseRedirect("/")
    else:
        uf = NewUserRegistrationForm()
        tf = NewActivityUserRegistrationForm()

    return render(request, "registration/register.html", {
        'userform': uf, 'activityform': tf, 'privacy': privacy,
        'helper': NewActivityUserRegistrationForm.helper
    })


def profile(request):
    """
    Update a User profile using built in Django Users Model if the user
    is logged in otherwise redirect them to registration version
    """
    if request.user.is_authenticated:
        obj = get_object_or_404(ActivityUser, user=request.user)
        form = RegistrationForm(request.POST or None, instance=obj,
                                initial={'username': request.user})

        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.error(
                    request, 'Your profile has been updated.',
                    fail_silently=False)

        return render(request, 'registration/profile.html', {
            'form': form, 'helper': RegistrationForm.helper
        })
    else:
        return HttpResponseRedirect('/accounts/register')


def admin_dashboard(request):
    """
    Admin dashboard view
    """
    nav_links = get_nav_links('Home')
    return render(
        request,
        'admin/landing_page.html',
        {'nav_links': nav_links}
    )


def admin_configurations(request):
    logged_activity_user = ActivityUser.objects.get(user=request.user)

    if request.method == 'POST' and request.is_ajax:
        data = request.POST

        model_updates = {
            'level_1_label': data.get('level_1_label'),
            'level_2_label': data.get('level_2_label'),
            'level_3_label': data.get('level_3_label'),
            'level_4_label': data.get('level_4_label'),
            'stakeholder_label': data.get('stakeholder_label'),
            'date_format': data.get('date_format'),
            # 'default_currency': data.get('default_currency')
        }
        organization = Organization.objects.filter(id=logged_activity_user.organization.id)
        updates = organization.update(**model_updates)
        if updates:
            organization_changes = Organization.objects.filter(
                id=logged_activity_user.organization.id)
            data = serializers.serialize('json', organization_changes)
            return HttpResponse(data, content_type="application/json")

    nav_links = get_nav_links('Configurations')
    return render(
        request,
        'admin/default_settings.html',
        {'nav_links': nav_links, 'organization': logged_activity_user.organization}
    )


def admin_profile_settings(request):
    nav_links = get_nav_links('Profile Settings')
    return render(
        request,
        'admin/profile_settings.html',
        {'nav_links': nav_links}
    )


def admin_user_management(request):
    nav_links = get_nav_links('User Management')
    return render(
        request,
        'admin/user_management.html',
        {'nav_links': nav_links}
    )


class BookmarkList(ListView):
    """
    Bookmark Report filtered by project
    """
    model = ActivityBookmarks
    template_name = 'registration/bookmark_list.html'

    def get(self, request, *args, **kwargs):
        get_user = ActivityUser.objects.all().filter(user=request.user)
        get_bookmarks = ActivityBookmarks.objects.all().filter(user=get_user)
        return render(request, self.template_name,
                      {'getBookmarks': get_bookmarks})


class BookmarkCreate(CreateView):
    """
    Using Bookmark Form for new bookmark per user
    """
    model = ActivityBookmarks
    template_name = 'registration/bookmark_form.html'
    guidance = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Bookmarks")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(BookmarkCreate, self).dispatch(request, *args, **kwargs)

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(BookmarkCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_initial(self):
        initial = {
            'user': self.request.user,
        }
        return initial

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Bookmark Created!')
        latest = ActivityBookmarks.objects.latest('id')
        redirect_url = '/bookmark_update/' + str(latest.id)
        return HttpResponseRedirect(redirect_url)

    form_class = BookmarkForm


class BookmarkUpdate(UpdateView):
    """
    Bookmark Form Update an existing site profile
    """
    model = ActivityBookmarks
    template_name = 'registration/bookmark_form.html'
    guidance = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="Bookmarks")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(BookmarkUpdate, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = {
            'user': self.request.user,
        }
        return initial

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Bookmark Updated!')
        latest = ActivityBookmarks.objects.latest('id')
        redirect_url = '/bookmark_update/' + str(latest.id)
        return HttpResponseRedirect(redirect_url)

    form_class = BookmarkForm


class BookmarkDelete(DeleteView):
    """
    Bookmark Form Delete an existing bookmark
    """
    model = ActivityBookmarks
    template_name = 'registration/bookmark_confirm_delete.html'
    success_url = "/bookmark_list"

    def dispatch(self, request, *args, **kwargs):
        return super(BookmarkDelete, self).dispatch(request, *args, **kwargs)

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Bookmark Deleted!')
        return self.render_to_response(self.get_context_data(form=form))

    form_class = BookmarkForm


def logout_view(request):
    """
    Logout a user
    """
    logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect("/")
