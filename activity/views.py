#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Q, Count
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import MultipleObjectsReturned

from indicators.models import CollectedData, Indicator
from workflow.models import (
    ProjectAgreement, ProjectComplete, Program,
    SiteProfile, Sector, Country, ActivityUser,
    ActivitySites, ActivityBookmarks, FormGuidance, Organization, UserInvite
)
from activity.tables import IndicatorDataTable
from activity.util import get_country, get_nav_links, send_invite_emails, \
    send_single_mail
from activity.forms import (
    RegistrationForm, BookmarkForm, OrganizationEditForm)
from activity.settings import PROJECT_ROOT
from django.core import serializers
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

APPROVALS = (
    ('in_progress', 'In Progress'),
    ('awaiting_approval', 'Awaiting Approval'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('new', 'New'),
)


@login_required(login_url='/accounts/login/')
def index(request, selected_countries=None, id=0, sector=0):
    """
    Home page
    get count of agreements approved and total for dashboard
    """

    # add program
    if request.method == 'POST' and request.is_ajax:
        return add_program(request)

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
        'get_site_profile': get_site_profile,
        'countries': user_countries,
        'selected_countries': selected_countries,
        'get_filtered_name': get_filtered_name,
        'get_sectors': get_sectors,
        'get_all_sectors': get_all_sectors,
        'sector': sector, 'table': table,
        'get_quantitative_data_sums': get_quantitative_data_sums,
        'count_evidence': count_evidence,
        'get_objectives': get_objectives,
        'selected_countries_list': selected_countries_list,
        'get_site_profile_indicator': get_site_profile_indicator,
        'get_agency_site': get_agency_site,
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
        'map_api_key': settings.GOOGLE_MAP_API_KEY
    })


@login_required(login_url='/accounts/login/')
def switch_organization(request, org_id):
    organization = Organization.objects.filter(id=int(org_id)).first()
    activity_user = ActivityUser.objects.filter(user=request.user).first()
    activity_user.organization = organization
    activity_user.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def activate_acccount(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        mail_subject = 'Welcome to Activity'
        data = {
            'user': user,
            'domain': request.build_absolute_uri('/').strip('/'),
        }
        email_txt = 'emails/registration/welcome.txt'
        email_html = 'emails/registration/welcome.html'

        send_single_mail(
            mail_subject,
            'Hikaya <team.hikaya@gmail.com>',
            [user.email],
            data, email_txt,
            email_html
        )
        # login(request, user)
        messages.success(request, 'Thanks, your email address has been confirmed')
        return render(request, 'registration/login.html', {'invite_uuid': 'none'})
    else:
        return HttpResponse('Activation link is invalid!')


class EmailError(Exception):
    """Existing Email Error"""
    pass


class MultipleUserNameError(Exception):
    """Existing Username Error"""
    pass


def register(request, invite_uuid):
    """
    Register a new User profile using built in Django Users Model
    """
    # redirect to homepage if user is logged in
    if request.user.is_authenticated:
        return redirect('/')

    # privacy = ActivitySites.objects.get(id=1)
    if request.method == 'POST':
        data = request.POST
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        username = data.get('username')
        email = data.get('email_address')
        password = data.get('password')

        try:
            if User.objects.get(email=email):
                invite_uuid = set_invite_uuid(invite_uuid)
                invite_uuid['message_email'] = 'email already exists !'
                return render(request, 'registration/register.html', invite_uuid)

        except User.DoesNotExist:
            try:
                user = User.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    email=email,
                    password=password,
                    is_active=False,
                )
            except IntegrityError:
                invite_uuid = set_invite_uuid(invite_uuid)
                invite_uuid['message_username'] = 'username already exists !'
                return render(request, 'registration/register.html', invite_uuid)

        if user:
            if invite_uuid != 'none':
                try:
                    invite = UserInvite.objects.get(invite_uuid=invite_uuid)
                    # activate invited user accounts
                    user.is_active = True
                    user.save()
                    activity_user = ActivityUser.objects.create(
                        user=user,
                        organization_id=invite.organization.id,
                        name='{} {}'.format(user.first_name, user.last_name)
                    )

                    # add organization to user organizations
                    activity_user.organizations.add(invite.organization)
                    if activity_user:
                        # delete the invitation
                        invite.delete()
                        return redirect('/accounts/login/')

                except UserInvite.DoesNotExist:
                    return HttpResponse({
                        'invalid_invite': 'Invalid invitation code. Please contact Organization admin'
                    })
            else:
                mail_subject = 'Please confirm your email address'
                data = {
                    'user': user,
                    'domain': request.build_absolute_uri('/').strip('/'),
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                    }
                email_txt = 'emails/registration/email_confirmation.txt'
                email_html = 'emails/registration/email_confirmation.html'

                send_single_mail(
                    mail_subject,
                    'Hikaya <team.hikaya@gmail.com>',
                    [email],
                    data,
                    email_txt,
                    email_html
                )

            activity_user = ActivityUser.objects.create(
                user=user,
                name='{} {}'.format(user.first_name, user.last_name)
            )
            if activity_user:
                return render(request, 'registration/confirm_email.html')

            else:
                return render(request, 'registration/register.html')

    else:

        invite_uuid = set_invite_uuid(invite_uuid)

        return render(request, 'registration/register.html', invite_uuid)


def set_invite_uuid(invite_uuid):
    if invite_uuid != 'none':
        try:
            invite = UserInvite.objects.get(invite_uuid=invite_uuid)
            invite_uuid = {'invite_uuid': invite_uuid,
                           'email_address': invite.email}
        except UserInvite.DoesNotExist:
            invite_uuid = {'invite_uuid': 'none'}
    else:
        invite_uuid = {'invite_uuid': 'none'}

    return invite_uuid


def user_login(request):
    """
    override django in-built login
    :param request:
    :return:
    """
    # redirect to homepage if user is logged in
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        data = request.POST
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            activity_user = ActivityUser.objects.filter(user=user).first()
            if activity_user.organization:
                return HttpResponseRedirect('/')
            else:
                return HttpResponseRedirect('/accounts/register/organization')

        else:
            return render(request, 'registration/login.html')
    return render(request, 'registration/login.html', {'invite_uuid': 'none'})


@login_required
def register_organization(request):
    """
    register organization
    : param request:
    : return org profile page
    """
    if request.method == 'POST':
        data = request.POST
        name = data.get('name')
        description = data.get('description')
        organization_url = data.get('organization_url')
        location = data.get('location')
        activity_url = data.get('activity_url')

        org = Organization.objects.create(
            name=name,
            description=description,
            organization_url=organization_url,
            location=location,
            activity_url=activity_url
            )
        if org:
            user = ActivityUser.objects.get(user=request.user)

            user.organization = org
            user.save()
            user.organizations.add(org)
            return redirect('/')
        else:
            return redirect('register_organization')
    else:
        return render(request, 'registration/organization_register.html')


@login_required(login_url='/accounts/login/')
def profile(request):
    """
    Update a User profile using built in Django Users Model if the user
    is logged in otherwise redirect them to registration page
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


@login_required(login_url='/accounts/login/')
def admin_dashboard(request):
    """
    Admin dashboard view
    """
    nav_links = get_nav_links('Usage')
    return render(
        request,
        'admin/landing_page.html',
        {'nav_links': nav_links}
    )


@login_required(login_url='/accounts/login/')
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
        organization = Organization.objects.filter(
            id=logged_activity_user.organization.id)
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
        {'nav_links': nav_links,
         'organization': logged_activity_user.organization}
    )


@login_required(login_url='/accounts/login/')
def admin_profile_settings(request):
    user = get_object_or_404(ActivityUser, user=request.user)
    organization = user.organization
    if request.method == 'POST':
        # form = OrganizationEditForm(request.FILES,
        #                             instance=organization)
        # if form.is_valid():
        data = request.POST
        print(data)
        organization.logo = request.FILES.get('organizationLogo')
        organization.name = data.get('name')
        organization.description = data.get('description')
        organization.save()
        user.organization = organization
        user.save()
        messages.error(
            request, 'Your organization logo has been updated.',
            fail_silently=False)

    nav_links = get_nav_links('Profile')
    return render(
        request,
        'admin/profile_settings.html',
        {'nav_links': nav_links, 'organization': organization}
    )


@login_required(login_url='/accounts/login/')
def admin_user_management(request, role, status):
    nav_links = get_nav_links('People')
    users = ActivityUser.objects.filter(
        organization=request.user.activity_user.organization)
    groups = Group.objects.all().distinct('name')

    user_organizations = request.user.activity_user.organizations
    if role != 'all':
        users = users.filter(user__groups__id__icontains=int(role))
    if status != 'all':
        status = True if status == 'active' else False
        users = users.filter(user__is_active=status)

    return render(request, 'admin/user_management.html', {
        'nav_links': nav_links,
        'users': users,
        'groups': groups,
        'organizations': user_organizations,
    })


@login_required(login_url='/accounts/login/')
def admin_user_invitations(request, organization):
    nav_links = get_nav_links('People')

    user_organizations = request.user.activity_user.organizations.all()
    invitations = UserInvite.objects.filter(
        organization__in=user_organizations)

    if int(organization) != 0:
        invitations = invitations.filter(organization_id=int(organization))

    return render(request, 'admin/user_invitations.html', {
        'nav_links': nav_links,
        'invitations': invitations,
        'organizations': user_organizations,
    })


@login_required(login_url='/accounts/login/')
def admin_user_edit(request, pk):
    """
    Edit user
    :param request:
    :param pk:
    :return:
    """
    nav_links = get_nav_links('People')
    obj = get_object_or_404(ActivityUser, pk=int(pk))
    form = RegistrationForm(request.POST or None, instance=obj,
                            initial={'username': request.user})

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.error(
                request, 'Your profile has been updated.',
                fail_silently=False)
            return redirect('/accounts/admin/users/all/all/')
    return render(request, 'admin/user_update_form.html', {
        'form': form,
        'helper': RegistrationForm.helper,
        'nav_links': nav_links
    })


@login_required(login_url='/accounts/login/')
def activate_deactivate_user(request, pk, status):
    """
    Deactivate or Activate Users
    :param request:
    :param pk:
    :param state:
    :return:
    """
    user = get_object_or_404(User, pk=pk)

    if status == 'activate':
        user.is_active = True
    else:
        user.is_active = False
    user.save()
    return redirect('/accounts/admin/users/all/all/')


@login_required(login_url='/accounts/login/')
def add_program(request):
    """ 
    Add program
    """
    data = request.POST
    activity_user = ActivityUser.objects.filter(user=request.user).first()
    program = Program(name=data.get(
        'program_name'), start_date=data.get('start_date'),
        end_date=data.get('end_date'), organization=activity_user.organization)

    try:
        program.save()

        sectors = Sector.objects.filter(id__in=data.getlist('sectors[]'))
        program.sector.set(sectors)

        # Return a "created" (201) response code.
        return HttpResponse(program)
    except Exception as ex:
        raise Exception(ex)


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
                      {'get_bookmarks': get_bookmarks})


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


@login_required
@csrf_protect
def invite_user(request):
    """
    invite user
    :param request: request context
    :return: success
    """
    if request.method == 'POST' and request.is_ajax:
        data = request.POST
        email_list = data.getlist('user_email_list[]')
        organization_id = int(data.get('organization'))
        failed_invites = []
        success_invites = []
        for email in email_list:
            try:
                if UserInvite.objects.get(email=email.lower()):
                    pass
            except MultipleObjectsReturned:
                pass
            except UserInvite.DoesNotExist:
                invite = UserInvite.objects.create(
                    email=email.lower(), organization_id=organization_id)
                if invite:
                    success_invites.append(invite)
                else:
                    failed_invites.append(email)

        # send invitation mails
        mail_subject = 'Invitation to Join Activity'
        email_from = 'team.hikaya@gmail.com'
        domain = request.build_absolute_uri('/').strip('/')
        data = {
            'link': '{}/accounts/register/user/'.format(domain)
        }

        if len(success_invites) > 0:
            send_invite_emails(mail_subject, email_from, success_invites, data)

        if len(failed_invites) == 0:
            return HttpResponse({'success': True})

        else:
            return HttpResponse({'success': False, 'failed': failed_invites})


@login_required(login_url='/accounts/login/')
@csrf_exempt
def delete_invitation(request, pk):
    try:
        invitation = UserInvite.objects.get(pk=int(pk))
        invitation.delete()
        return HttpResponse({'success': True})
    except UserInvite.DoesNotExist:
        pass
