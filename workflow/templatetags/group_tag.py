#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.contrib.auth.models import Group

from django import template
from django.template.defaultfilters import stringfilter

from workflow.models import ActivityUserOrganizationGroup

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False


@register.filter(name='has_org_access')
def has_access(activity_user, group):
    user_org_access = ActivityUserOrganizationGroup.objects.filter(
        activity_user_id=activity_user.id,
        organization_id=activity_user.organization.id
    )

    groups = user_org_access.values_list('groups__name', flat=True)
    print('Groups:::::::::', groups)

    if group in groups:
        return True
    return False


@register.filter
@stringfilter
def template_exists(template_name="links.html"):
    try:
        template.loader.get_template(template_name)
        return True
    except template.TemplateDoesNotExist:
        return False
