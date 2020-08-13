#!/usr/bin/python3
# -*- coding: utf-8 -*-
from smtplib import (SMTPRecipientsRefused)

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.template.response import TemplateResponse
from django.views.generic import RedirectView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from django.contrib import messages
from django.contrib.auth import (
    logout, authenticate,
    login, update_session_auth_hash,)
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import PasswordChangeForm

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db import IntegrityError
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import MultipleObjectsReturned

from indicators.models import (
    CollectedData, Indicator,
    DataCollectionFrequency,
)
from workflow.models import (
    ProjectAgreement, ProjectComplete, Program,
    SiteProfile, Sector, ActivityUser, ActivityBookmarks, FormGuidance,
    Organization, UserInvite, Stakeholder, Contact, Documentation,
    ActivityUserOrganizationGroup,
)
from activity.util import get_nav_links, send_invite_emails, \
    send_single_mail
from activity.forms import (
    RegistrationForm, BookmarkForm, NewUserRegistrationForm)
from django.core import serializers
from .tokens import account_activation_token
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings
from .forms import HTMLPasswordResetForm

APPROVALS = (
    ('in_progress', 'In Progress'),
    ('awaiting_approval', 'Awaiting Approval'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('new', 'New'),
)


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'
    login_url = '/accounts/login/'

    def get(self, request, program_id=0, *args, **kwargs):
        # set the selected program
        selected_program = Program.objects.filter(id=program_id).first()

        # get programs belonging to the current organizatiom
        get_programs = Program.objects.filter(
            organization=request.user.activity_user.organization).exclude(
            name__isnull=True).exclude(name__exact='')

        if int(program_id) == 0:
            org_id = request.user.activity_user.organization.id
            org_q = Q(organization__id=request.user.activity_user.organization.id)
            prog_q = Q(program__organization=request.user.activity_user.organization)
        else:
            org_id = selected_program.organization.id
            org_q = Q(program__id=selected_program.id)
            prog_q = Q(program__id=program_id)

        locations = SiteProfile.objects.filter(organizations__id=org_id)

        stakeholders = Stakeholder.objects.filter(org_q).distinct()
        contacts = Contact.objects.filter(organization__id=org_id)
        projects = ProjectAgreement.objects.filter(prog_q)
        indicators = Indicator.objects.filter(prog_q).distinct().order_by('-id')
        collected_data = CollectedData.objects.filter(prog_q)
        documents = Documentation.objects.filter(prog_q)
        projects_awaiting_approval = ProjectAgreement.objects.filter(prog_q & Q(approval='awaiting approval'))
        projects_approved = ProjectAgreement.objects.filter(prog_q & Q(approval='approved'))
        projects_rejected = ProjectAgreement.objects.filter(prog_q & Q(approval='rejected'))
        projects_new = ProjectAgreement.objects.filter(prog_q & (
                Q(approval='') | Q(approval=None) | Q(approval__iexact='new')))
        projects_in_progress = ProjectAgreement.objects.filter(prog_q & Q(approval='in progress'))

        projects_tracking = ProjectComplete.objects.filter(prog_q)
        indicators_kpi = indicators.filter(key_performance_indicator=True)
        latest_indicators = indicators.filter(key_performance_indicator=True)[:10]
        get_all_sectors = Sector.objects.all()

        context = {
            'selected_program': selected_program,
            'get_all_sectors': get_all_sectors,
            'get_programs': get_programs,
            'get_projects': projects,
            'get_indicators': indicators,
            'get_latest_indicators': latest_indicators,
            'get_indicators_kpi_count': indicators_kpi.count(),
            'get_collected_data_count': collected_data.count(),
            'get_stakeholders_count': stakeholders.count(),
            'get_contacts_count': contacts.count(),
            'get_documents_count': documents.count(),
            'get_active_locations_count': locations.filter(status=True).count(),
            'get_locations_count': locations.count(),
            'get_locations': locations,
            'get_projects_awaiting_approval_count': projects_awaiting_approval.count(),
            'get_projects_approved_count': projects_approved.count(),
            'get_projects_rejected_count': projects_rejected.count(),
            'get_projects_new_count': projects_new.count(),
            'get_projects_in_progress_count': projects_in_progress.count(),
            'get_projects_tracking_count': projects_tracking.count(),
            'map_api_key': settings.GOOGLE_MAP_API_KEY
        }

        return TemplateResponse(request, self.template_name, context)


@login_required(login_url='/accounts/login/')
def switch_organization(request, org_id):
    organization = Organization.objects.filter(id=int(org_id)).first()
    activity_user = ActivityUser.objects.filter(user=request.user).first()
    activity_user.organization = organization
    activity_user.save()

    return redirect('/')


def activate_acccount(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        # send welcome mail
        send_welcome_email(request, user)

        # login(request, user)
        messages.success(
            request, 'Thanks, your email address has been confirmed')
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

    # check if a user is invited
    if invite_uuid != 'none':
        try:
            user_invite = UserInvite.objects.get(invite_uuid=invite_uuid)
        except UserInvite.DoesNotExist:
            return render(request, 'admin/invalid_invitation.html')

    else:
        user_invite = None

    # privacy = ActivitySites.objects.get(id=1)
    if request.method == 'POST':
        data = request.POST
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        username = data.get('username')
        # always change the mail address to LowerCase
        email = data.get('email_address').lower()
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

            except ValueError:
                messages.error(request, 'Please ensure you fill in all required fields')
                return render(request, 'registration/register.html')

        if user:
            if user_invite is not None:
                # activate invited user accounts
                user.is_active = True
                user.save()
                activity_user = ActivityUser.objects.create(
                    user=user,
                    organization_id=user_invite.organization.id,
                    name='{} {}'.format(user.first_name, user.last_name)
                )

                # add organization to user organizations
                activity_user.organizations.add(user_invite.organization)

                # define user organization access groups
                user_org_access = ActivityUserOrganizationGroup.objects.create(
                    activity_user=activity_user,
                    organization=user_invite.organization,
                )
                # set default permission to editor on invite
                group = Group.objects.get(name='Editor')
                user_org_access.group = group
                user_org_access.save()
                if activity_user:
                    # delete the invitation
                    user_invite.delete()

                    # send welcome email
                    send_welcome_email(request, user)

                    messages.success(
                        request, 'Thanks, your email address has been confirmed')
                    return render(request, 'registration/login.html', {'invite_uuid': 'none'})

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

                try:
                    send_single_mail(
                        mail_subject,
                        'team.hikaya@gmail.com',
                        [email],
                        data,
                        email_txt,
                        email_html
                    )
                except SMTPRecipientsRefused:
                    # delete user if an email can't be sent
                    user.delete()
                    messages.error(
                        request,
                        'We can not confirmation mail, please check email address and try again',
                        fail_silently=True
                    )
                    return render(request, 'registration/register.html')

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


def send_welcome_email(request, user):
    mail_subject = 'Welcome to Activity'
    data = {'user': user, 'domain': request.build_absolute_uri('/').strip('/')}
    email_txt = 'emails/registration/welcome.txt'
    email_html = 'emails/registration/welcome.html'

    send_single_mail(
        mail_subject,
        'team.hikaya@gmail.com',
        [user.email],
        data,
        email_txt,
        email_html
    )


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


class UserLogin(View):
    """User login class view"""

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'registration/login.html', {'invite_uuid': 'none'})

    def post(self, request, *args, **kwargs):
        data = request.POST
        username = data.get('username', None)
        password = data.get('password', None)
        # check if user is active
        user = User.objects.filter(Q(username__iexact=username) | Q(email__iexact=username.lower())).first()
        if not user:
            messages.error(request, 'Incorrect credentials.', fail_silently=True)
            return render(request, 'registration/login.html')

        if not user.is_active:
            messages.error(request, 'Please verify your email address then try again.', fail_silently=True)
            return render(request, 'registration/login.html')

        # proceed to authenticate the user
        user = authenticate(username=user.username, password=password)
        if not user:
            messages.error(request, 'Incorrect credentials.', fail_silently=True)
            return render(request, 'registration/login.html')

        login(request, user)
        activity_user = ActivityUser.objects.filter(user=user).first()
        if activity_user.organization:
            return HttpResponseRedirect('/')

        return HttpResponseRedirect('/accounts/register/organization')


class RegisterOrganization(LoginRequiredMixin, View):
    """Register organization view"""

    def get(self, request, *args, **kwargs):
        return render(request, 'registration/organization_register.html')

    def post(self, request, *args, **kwargs):
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
            # add organization to the current user
            user.organization = org
            user.save()
            user.organizations.add(org)

            # define user organization access groups
            user_org_access = ActivityUserOrganizationGroup.objects.create(
                activity_user=user,
                organization=org,
            )
            group = Group.objects.get(name='Owner')
            user_org_access.group = group
            user_org_access.save()

            return redirect('/')
        else:
            return redirect('register_organization')


@login_required(login_url='/accounts/login/')
def profile(request):
    """
    Update a User profile using built in Django Users Model if the user
    is logged in otherwise redirect them to registration page
    """
    if request.user.is_authenticated:
        activity_user_obj = get_object_or_404(ActivityUser, user=request.user)
        user_obj = activity_user_obj.user
        form = RegistrationForm(
            request.POST or None,
            instance=activity_user_obj,
            initial={'username': request.user}
        )
        user_form = NewUserRegistrationForm(
            request.POST or None, instance=user_obj)

        if request.method == 'POST':
            data = request.POST
            activity_user_object = {
                'employee_number': data.get('employee_number'),
                'organization': data.get('organization'),
                'title': data.get('title')
            }

            user_object = {
                'first_name': data.get('first_name'),
                'last_name': data.get('last_name'),
                'email': data.get('email'),
                'username': data.get('username')
            }
            # save user
            User.objects.filter(pk=user_obj.id).update(**user_object)
            user = User.objects.get(pk=request.user.id)
            if user:

                # save Activity user after updating name
                activity_user = ActivityUser.objects.get(user=request.user)
                activity_user.organization = Organization.objects.get(
                    pk=int(activity_user_object['organization']))
                activity_user.name = '{} {}'.format(
                    user.first_name, user.last_name)
                activity_user.save()

            messages.success(
                request, 'Your profile has been updated.', fail_silently=True)

        return render(request, 'registration/profile.html', {
            'form': form,
            'user_form': user_form,
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
        {'nav_links': nav_links, 'active': 'usage'}
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
            'site_label': data.get('site_label'),
            'indicator_label': data.get('indicator_label'),
            'form_label': data.get('form_label'),
            'stakeholder_label': data.get('stakeholder_label'),
            'date_format': data.get('date_format'),
            'individual_label': data.get('individual_label'),
            'training_label': data.get('training_label'),
            'distribution_label': data.get('distribution_label'),
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
         'organization': logged_activity_user.organization, 'active': 'configurations'}
    )


@login_required(login_url='/accounts/login/')
def admin_profile_settings(request):
    user = get_object_or_404(ActivityUser, user=request.user)
    organization = user.organization
    # reset logo
    if request.GET.get('reset_logo'):
        organization = Organization.objects.get(pk=user.organization.id)
        organization.logo = ''
        organization.save()

    if request.method == 'POST':
        # form = OrganizationEditForm(request.FILES,
        #                             instance=organization)
        # if form.is_valid():
        data = request.POST
        organization.logo = request.FILES.get('organizationLogo')
        organization.name = data.get('name')
        organization.description = data.get('description')
        organization.save()
        user.organization = organization
        user.save()
        messages.success(
            request, 'Your organization logo has been updated.',
            fail_silently=False)

    nav_links = get_nav_links('Profile')
    return render(
        request,
        'admin/profile_settings.html',
        {
            'nav_links': nav_links,
            'organization': organization,
            'active': 'profile'
        }
    )


@login_required(login_url='/accounts/login/')
def admin_user_management(request, role, status):
    nav_links = get_nav_links('People')
    users = ActivityUser.objects.filter(
        organizations__id=request.user.activity_user.organization.id
    ).exclude(user__is_superuser=True)
    groups = Group.objects.all().distinct('name')

    # get owner orgs
    user_org_group_ids = ActivityUserOrganizationGroup.objects.filter(
        activity_user=request.user.activity_user,
        group__name='Owner'
    ).values_list('organization__id', flat=True)

    user_organizations = Organization.objects.filter(id__in=user_org_group_ids)
    if role != 'all':
        get_org_users_by_roles = ActivityUserOrganizationGroup.objects.filter(
            organization__id=request.user.activity_user.organization.id,
            group__id=int(role)
        ).values_list('activity_user__id')

        users = users.filter(
            id__in=get_org_users_by_roles
        )

    if status != 'all':
        status = True if status == 'active' else False
        get_org_users_by_roles = ActivityUserOrganizationGroup.objects.filter(
            organization__id=request.user.activity_user.organization.id,
            is_active=status
        ).values_list('activity_user__id')
        users = users.filter(id__in=get_org_users_by_roles)

    return render(request, 'admin/user_management.html', {
        'nav_links': nav_links,
        'users': users,
        'groups': groups,
        'organizations': user_organizations,
        'active': 'people'
    })


@login_required(login_url='/accounts/login/')
def admin_component_admin(request):
    user = ActivityUser.objects.filter(user=request.user).first()
    stakeholders = Stakeholder.objects.filter(organization=user.organization)
    nav_links = get_nav_links('Components')
    return render(
        request,
        'admin/component_admin.html',
        {
            'nav_links': nav_links,
            'get_stakeholders': stakeholders,
            'active': 'components'
        }
    )


@login_required(login_url='/accounts/login/')
def admin_indicator_config(request):
    user = get_object_or_404(ActivityUser, user=request.user)
    organization = user.organization
    get_collection_frequencies = DataCollectionFrequency.objects.all()

    nav_links = get_nav_links('Indicators')
    return render(
        request,
        'admin/indicator_configs.html',
        {
            'nav_links': nav_links,
            'organization': organization,
            'get_collection_frequencies': get_collection_frequencies,
            'active': 'indicators'
        }
    )


@login_required(login_url='/accounts/login/')
def admin_map_settings(request):
    user = get_object_or_404(ActivityUser, user=request.user)
    organization = user.organization
    # reset logo
    # if request.GET.get('reset_logo'):
    #     organization = Organization.objects.get(pk=user.organization.id)
    #     organization.logo = ''
    # organization.save()

    if request.method == 'POST':
        data = request.POST
        organization.country_code = data.get('country_code')
        organization.location_description = data.get('location_description')
        organization.latitude = data.get('latitude')
        organization.longitude = data.get('longitude')
        organization.zoom = data.get('zoom')
        organization.save()
        user.organization = organization
        user.save()

    nav_links = get_nav_links('Maps')
    return render(
        request,
        'admin/map_settings.html',
        {
            'nav_links': nav_links,
            'organization': organization,
            'active': 'maps'
        }
    )


@login_required(login_url='/accounts/login/')
def admin_form_library_settings(request):
    nav_links = get_nav_links('Form Library')
    return render(
        request,
        'admin/form_library_settings.html',
        {
            'nav_links': nav_links,
            'active': 'form_library'
        }
    )


@login_required(login_url='/accounts/login/')
def admin_workflow_settings(request):
    nav_links = get_nav_links('Workflows')
    return render(
        request,
        'admin/workflow_settings.html',
        {
            'nav_links': nav_links,
            'active': 'workflows'
        }
    )


@login_required(login_url='/accounts/login/')
def admin_indicator_settings(request):
    user = get_object_or_404(ActivityUser, user=request.user)
    organization = user.organization

    # ! Unused variable
    # nav_links = get_nav_links('Indicator')

    return render(
        request,
        'admin/indicator_settings.html',
        {
            'organization': organization,
            'active': 'indicator_settings'
        }
    )


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
    activity_user_obj = get_object_or_404(ActivityUser, pk=int(pk))
    user_obj = activity_user_obj.user

    form = RegistrationForm(request.POST or None, instance=activity_user_obj,
                            initial={'username': request.user})
    user_form = NewUserRegistrationForm(
        request.POST or None, instance=user_obj)

    if request.method == 'POST':
        data = request.POST
        activity_user_object = {
            'employee_number': data.get('employee_number'),
            'organization': data.get('organization'),
            'title': data.get('title')
        }

        user_object = {
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'email': data.get('email'),
            'username': data.get('username')
        }
        # save user
        User.objects.filter(pk=user_obj.id).update(**user_object)
        user = User.objects.get(pk=user_obj.pk)
        if user:
            # save Activity user after updating name
            activity_user = activity_user_obj
            activity_user.employee_number = activity_user_object['employee_number']
            activity_user.organization = Organization.objects.get(
                pk=int(activity_user_object['organization']))
            activity_user.title = activity_user_object['title']
            activity_user.name = '{} {}'.format(
                user.first_name, user.last_name)
            activity_user.save()

        messages.success(
            request, 'Your profile has been updated.',
            fail_silently=False)
        return redirect('/accounts/admin/users/all/all/')
    return render(request, 'admin/user_update_form.html', {
        'form': form,
        'user_form': user_form,
        'helper': RegistrationForm.helper,
        'nav_links': nav_links
    })


@login_required(login_url='/accounts/login/')
def update_user_access(request, pk, status):
    """
    Deactivate or Activate Users
    :param request:
    :param pk:
    :param status:
    """
    user_grp = ActivityUserOrganizationGroup.objects.filter(
        activity_user__id=int(pk),
        organization_id=request.user.activity_user.organization.id).first()
    if user_grp is None:
        activity_user = ActivityUser.objects.get(pk=int(pk))
        group = Group.objects.filter(name='Editor').first()
        user_grp = ActivityUserOrganizationGroup.objects.create(
            activity_user=activity_user,
            organization=request.user.activity_user.organization,
            group=group
        )

    if status == 'activate':
        user_grp.is_active = True
        user_grp.save()

    elif status == 'deactivate':
        user_grp.is_active = False
        user_grp.save()

    else:
        new_gp = Group.objects.get(name=status)
        activity_user = ActivityUser.objects.get(pk=int(pk))
        user_org_access = ActivityUserOrganizationGroup.objects.filter(
            activity_user_id=activity_user.id,
            organization_id=request.user.activity_user.organization.id).first()
        user_org_access.group = new_gp
        user_org_access.save()

    return redirect('/accounts/admin/users/all/all/')


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

    # New Invitations
    if request.method == 'POST' and request.is_ajax:
        data = request.POST
        email_list = data.getlist('user_email_list[]')
        organization_id = int(data.get('organization'))
        failed_invites = []
        success_invites = []
        url_route = ''
        for email in email_list:
            try:
                check_invite = UserInvite.objects.get(email=email.lower())
                if check_invite:
                    redirect(
                        '/accounts/admin/invitations/?resend_invite={}'.format(
                            check_invite.invite_uuid)
                    )

            except MultipleObjectsReturned:
                redirect(
                    '/accounts/admin/invitations/?resend_invite={}'.format(
                        check_invite.invite_uuid)
                )

            except UserInvite.DoesNotExist:
                invite = None
                try:
                    check_user = User.objects.get(email=email)
                    if check_user:
                        user_orgs = check_user.activity_user.organizations.values_list(
                            'id', flat=True)
                        if organization_id in user_orgs:
                            organization = Organization.objects.get(id=organization_id)
                            return JsonResponse(
                                {'user_exists': True, 'organization': organization.name}
                            )
                        else:
                            url_route = '/accounts/join/organization/'

                except User.DoesNotExist:
                    url_route = '/accounts/register/user/'

                # create an invitation
                if url_route is not None:

                    invite = UserInvite.objects.create(
                        email=email.lower(),
                        organization_id=organization_id
                    )

                if invite:
                    success_invites.append(invite)
                else:
                    failed_invites.append(email)

        # send invitation mails
        mail_subject = 'Invitation to Join Activity'
        email_from = 'team.hikaya@gmail.com'
        domain = request.build_absolute_uri('/').strip('/')
        data = {
            'link': '{}{}'.format(domain, url_route)
        }

        if len(success_invites) > 0:
            send_invite_emails(mail_subject, email_from, success_invites, data)

        if len(failed_invites) == 0:
            return HttpResponse({'success': True})

        else:
            return HttpResponse({'success': False, 'failed': failed_invites})


class UserInviteView(View):
    """
    User invitation class view
    """

    def get(self, request, *args, **kwargs):

        # revoke existing invite
        if self.request.GET.get('revoke_invite', None) is not None:
            invitation_uuid = self.request.GET.get('revoke_invite')
            invitation = self.delete_invitation(invitation_uuid)

        # resend existing invite
        if self.request.GET.get('resend_invite', None) is not None:
            invitation_uuid = self.request.GET.get('resend_invite')
            invitation = self.resend_invitation(invitation_uuid)

        return HttpResponse(invitation)

    def create_new_invitation(self, data):
        """
        Send new invitations
        :param data: post data
        """
        email_list = data.getlist('user_email_list[]')
        organization_id = int(data.get('organization'))
        failed_invites = []
        success_invites = []
        url_route = ''
        for email in email_list:
            try:
                if UserInvite.objects.get(email=email.lower()):
                    pass  # purpose to implement resend invite
            except MultipleObjectsReturned:
                pass
            except UserInvite.DoesNotExist:
                invite = UserInvite.objects.create(
                    email=email.lower(), organization_id=organization_id)

                try:
                    if User.objects.get(email=email):
                        url_route = '/accounts/join/organization/'
                except User.DoesNotExist:
                    url_route = '/accounts/register/user/'
                if invite:
                    success_invites.append(invite)
                else:
                    failed_invites.append(email)
        if len(success_invites) > 0:
            self.send_invitation_mail(success_invites, url_route)

        if len(failed_invites) == 0:
            return {'success': True}

        else:
            return {'success': False}

    def resend_invitation(self, invite):
        """
        Resend invitations
        """
        user_invite = UserInvite.objects.get(invite_uuid=invite)
        try:
            if User.objects.get(email=user_invite.email):
                url_route = '/accounts/join/organization/'
        except User.DoesNotExist:
            url_route = '/accounts/register/user/'

        self.send_invitation_mail([user_invite], url_route)

        return {'success': True}

    @staticmethod
    def delete_invitation(invite_uuid):
        """
        Revoke Invitations
        :param invite_uuid:
        """
        try:
            invitation = UserInvite.objects.get(invite_uuid=invite_uuid)
            invitation.delete()
            return {'success': True}

        except UserInvite.DoesNotExist:
            return {'success': False}

    def send_invitation_mail(self, user_invites, link):
        """
        Send invitation mail
        :param user_invites:
        :param link:
        """
        mail_subject = 'Invitation to Join Activity'
        email_from = 'team.hikaya@gmail.com'
        domain = self.request.build_absolute_uri('/').strip('/')
        data = {'link': '{}{}'.format(domain, link)}

        send_invite_emails(
            mail_subject,
            email_from,
            user_invites,
            data
        )


def invite_existing_user(request, invite_uuid):
    """
    Invite an existing user
    :param request:
    :param invite_uuid:
    :return:
    """
    try:
        invite = UserInvite.objects.get(invite_uuid=invite_uuid)
        try:
            user = User.objects.get(email=invite.email)
            activity_user = ActivityUser.objects.filter(user=user).first()
            if activity_user:
                # Accepting the invite of an existing user
                activity_user.organization = invite.organization
                activity_user.save()
                activity_user.organizations.add(invite.organization)

                # delete the invite
                invite.delete()
                # define user organization access groups
                user_org_access = ActivityUserOrganizationGroup.objects.create(
                    activity_user=activity_user,
                    organization=invite.organization,
                )
                # set default permission to editor on invite
                group = Group.objects.get(name='Editor')
                user_org_access.group = group
                user_org_access.save()

                messages.success(request,
                                 'You have successfully joined {}'.format(invite.organization.name))
                # TODO this renders the login form even if the user is logged in
                return render(request, 'registration/login.html', {'invite_uuid': invite_uuid})

            # if user is not found
            messages.error(request, 'Error, there was an error adding you to {}'.format(
                invite.organization.name))
            return render(request, 'registration/login.html', {'invite_uuid': invite_uuid})
        except User.DoesNotExist:
            messages.error(
                request,
                'Error, there was an error adding you to {}'.format(invite.organization.name))
            return render(request, 'registration/login.html', {'invite_uuid': invite_uuid})

    except UserInvite.DoesNotExist:
        messages.error(request, 'Error, this invitation is no longer valid')
        return render(request, 'registration/login.html', {'invite_uuid': invite_uuid})


class PasswordReset(RedirectView):
    """
    Override Password Reset View
    forcing to use HTML email template (param: html_email_template_name
    """
    is_admin_site = False
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.html'
    token_generator = default_token_generator
    post_reset_redirect = '/accounts/password_reset/done/'
    from_email = None,
    current_app = None,
    extra_context = None

    def get(self, request, *args, **kwargs):
        form = HTMLPasswordResetForm()
        context = {
            'form': form,
        }
        if self.extra_context is not None:
            context.update(self.extra_context)
        return TemplateResponse(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = HTMLPasswordResetForm(request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': self.token_generator,
                'from_email': self.from_email,
                'email_template_name': self.email_template_name,
                'subject_template_name': self.subject_template_name,
                'request': request,
            }
            if self.is_admin_site:
                opts = dict(opts, domain_override=request.get_host())
            form.save(**opts)
            return HttpResponseRedirect(self.post_reset_redirect)
        context = {
            'form': form,
        }
        if self.extra_context is not None:
            context.update(self.extra_context)
        return TemplateResponse(request, self.template_name, context,
                                current_app=self.current_app)


def change_password(request):
    """
    change password view
    :param request:
    :return:
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Important!!! keep the user logged in after changing the password
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'registration/change_password.html', {
        'form': form
    })
