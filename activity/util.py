import os
import sys

import unicodedata
import json
import requests

from django.core import mail
from workflow.models import Country, ActivityUser, ActivitySites, Organization
from django.contrib.auth.models import User
from django.core.mail import mail_admins, EmailMessage, EmailMultiAlternatives
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test
from django.template import loader


# CREATE NEW DATA DICTIONARY OBJECT
def silo_to_dict(silo):
    parsed_data = {}
    key_value = 1
    for d in silo:
        label = unicodedata.normalize(
            'NFKD', d.field.name).encode('ascii', 'ignore')
        value = unicodedata.normalize(
            'NFKD', d.char_store).encode('ascii', 'ignore')
        # row = unicodedata.normalize(
        #     'NFKD', d.row_number).encode('ascii', 'ignore')
        parsed_data[key_value] = {label: value}

        key_value += 1

    return parsed_data


def get_country(user):
    """
    Returns the object the view is displaying.
    """
    user_countries = ActivityUser.objects.all().filter(
        user__id=user.id).values('countries')

    get_countries = Country.objects.all().filter(id__in=user_countries)

    return get_countries


def get_organizations(user):
    """
    Returns the object the view is displaying.
    """
    user_organizations = ActivityUser.objects.all().filter(
        user__id=user.id).values('organizations')

    get_user_organizations = Organization.objects.all().filter(id__in=user_organizations)

    return get_user_organizations


def email_group(country, group, link, subject, message, submiter=None):
    # email incident to admins in each country assoicated
    # with the projects program
    for single_country in country.all():
        country = Country.objects.all().filter(country=single_country)
        get_group_emails = User.objects.all().filter(
            activity_user=group,
            activity_user__country=country).values_list('email', flat=True)
        email_link = link
        formatted_email = email_link
        subject = str(subject)
        message = str(message) + formatted_email

        to = [str(item) for item in get_group_emails]
        if submiter:
            to.append(submiter)
        email = EmailMessage(subject, message, 'admin@hikaya.io', to)
        email.send()
    mail_admins(subject, message, fail_silently=False)


def get_table(url, data=None):
    """
    Get table data from a Silo.  First get the Data url from the silo details
    then get data and return it

    :param url: URL to silo meta detail info
    :param data:
    :return: json dump of table data
    """
    token = ActivitySites.objects.get(site_id=1)
    if token.activity_tables_token:
        headers = {'content-type': 'application/json',
                   'Authorization': 'Token ' + token.activity_tables_token}
    else:
        headers = {'content-type': 'application/json'}
        print("Token Not Found")

    response = requests.get(url, headers=headers, verify=True)
    if data:
        data = json.loads(response.content['data'])
    else:
        data = json.loads(response.content)
    return data


def user_to_activity(user, response):

    # Add a google auth user to the Activity profile
    default_country = Country.objects.first()
    userprofile, created = ActivityUser.objects.get_or_create(
        user=user)

    userprofile.country = default_country

    userprofile.name = response.get('displayName')

    userprofile.email = response.get('emails["value"]')

    userprofile.save()
    # add user to country permissions table
    userprofile.countries.add(default_country)


def group_excluded(*group_names, url):
    # If user is in the group passed in permission denied
    def in_groups(u):
        if u.is_authenticated:
            if not bool(u.groups.filter(name__in=group_names)):
                return True
            raise PermissionDenied
        return False

    return user_passes_test(in_groups)


def group_required(*group_names, url):
    # Requires user membership in at least one of the groups passed in.
    def in_groups(u):
        if u.is_authenticated():
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
            raise PermissionDenied
        return False
    return user_passes_test(in_groups)


def get_nav_links(nav):
    nav_links = [
        {
            'label': 'Profile',
            'status': '',
            'link': '/accounts/admin/profile_settings'
        },
        {
            'label': 'Configurations',
            'status': '',
            'link': '/accounts/admin/configurations'
        },
        {
            'label': 'People',
            'status': '',
            'link': '/accounts/admin/users/all/all/'
        },
        {
            'label': 'Usage',
            'status': '',
            'link': '/accounts/admin_dashboard'
        },
        {
            'label': 'Workflows',
            'status': '',
            'link': '/accounts/admin/workflow_settings'
        },
        {
            'label': 'Indicators',
            'status': '',
            'link': '/accounts/admin/indicator_configs_admin'
        },
        {
            'label': 'Components',
            'status': '',
            'link': '/accounts/admin/component_admin'
        },
        {
            'label': 'Maps',
            'status': '',
            'link': '/accounts/admin/map_settings'
        },
    ]
    for item in nav_links:
        if item['label'] == nav:
            item['status'] = 'active'
    return nav_links


def send_invite_emails(subject, email_from, email_to, data):
    """
    send mass emails
    :param subject: email subject
    :param email_from: email sender
    :param email_to: recipients list
    :param data: context data
    """
    if len(email_to) > 1:
        connection = mail.get_connection()
        messages = list()
        for email in email_to:
            link = '{}{}/'.format(data['link'], email.invite_uuid)
            email_context = {
                'organization': email.organization.name,
                'link': link,
                'email': email.email
            }
            email_txt = loader.render_to_string('emails/invite.txt', email_context)
            email_html = loader.get_template('emails/invite.html')
            email_html_content = email_html.render(email_context)
            msg = EmailMultiAlternatives(subject, email_txt,
                                         'Hikaya <{}>'.format(email_from), [email.email])
            msg.attach_alternative(email_html_content, "text/html")
            messages.append(msg)

        connection.send_messages(messages)
    else:
        link = '{}{}/'.format(data['link'], email_to[0].invite_uuid)
        email_context = {
            'organization': email_to[0].organization.name,
            'link': link,
            'email': email_to[0].email
        }
        email_txt = loader.render_to_string('emails/invite.txt', email_context)
        email_html = loader.get_template('emails/invite.html')
        email_html_content = email_html.render(email_context)
        msg = EmailMultiAlternatives(subject, email_txt,
                                     'Hikaya <{}>'.format(email_from), [email_to[0].email])
        msg.attach_alternative(email_html_content, "text/html")

        msg.send()


def send_single_mail(subject, email_from, email_to, data, email_txt, email_html):
    """
    Send single email
    :param subject: email subject
    :param email_from: email sender
    :param email_to: recipients list
    :param data: context data
    :param email_txt: text email template
    :param email_html: html email template
    """
    email_context = data
    email_txt = loader.render_to_string(email_txt, email_context)
    email_html = loader.get_template(email_html)
    email_html_content = email_html.render(email_context)

    msg = EmailMultiAlternatives(
        subject,
        email_txt,
        'Hikaya <{}>'.format(email_from),
        email_to
    )
    msg.attach_alternative(email_html_content, "text/html")
    msg.send()


def user_signup_notification(user):
    url = os.environ.get('SLACK_WEBHOOK_URL')
    message = ("A new user has signed up on activity")
    title = ("New User Sign Up :zap:")
    date = user.date_joined.strftime('%m-%d-%Y')

    slack_data = {
        "username": "new-user-notification",
        "icon_emoji": ":bell:",
        "attachments": [
            {
                "color": "#25ced1",
                "fields": [
                    {
                        "title": title,
                        "value": message,
                    },
                    {
                        "title": "Username:",
                        "value": user.username,
                    },
                    {
                        "title": "Email:",
                        "value": user.email,
                    },
                    {
                        "title": "Date Joined:",
                        "value": date,
                    }
                ],
            },
        ]
    }
    byte_length = str(sys.getsizeof(slack_data))
    headers = {'Content-Type': "application/json", 'Content-Length': byte_length}
    response = requests.post(url, data=json.dumps(slack_data), headers=headers)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
