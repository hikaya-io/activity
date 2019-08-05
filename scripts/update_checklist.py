#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
import json data from API
IMPORTANT!! you must turn off pagination for this to work from a URL
and get all country records
Install module django-extensions
Runs twice via function calls at bottom once
"""
from workflow.models import ProjectAgreement, Checklist, ChecklistItem
from django.db import connection

cursor = connection.cursor()


def run():
    print("Uploading Country Admin data")


def get_all_data():
    # get all the projects and loop over them
    get_projects = ProjectAgreement.objects.all()
    for item in get_projects:
        # if the project doesn't have a checklist create one
        try:
            get_checklist = Checklist.objects.get(agreement=item)
        except Checklist.DoesNotExist:
            get_checklist = Checklist(agreement=item)
            get_checklist.save()

            update_items(get_checklist)
        # if it does update the items in the checklist to include all
        # the new globals
        update_items(get_checklist)
        print(item)


def update_items(checklist):

    get_checklist = Checklist.objects.get(id=checklist.id)
    get_globals = ChecklistItem.objects.all().filter(global_item=True)
    for item in get_globals:
        look_for_existing = ChecklistItem.objects.all().filter(
            checklist=get_checklist, item=item)
        print(item)
        if look_for_existing:
            print("dupe do nothing")
        else:
            ChecklistItem.objects.create(
                checklist=get_checklist, item=item.item)
            print(item)


get_all_data()
