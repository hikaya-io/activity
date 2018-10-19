"""
import json data from API
IMPORTANT!! you must turn off pagination for this to work from a URL and get all
country records
Install module django-extensions
Runs twice via function calls at bottom once
"""
from django.db import connection, transaction

cursor = connection.cursor()
from os.path import exists
import csv
import unicodedata
import sys
import urllib2
from datetime import date
from workflow.models import ProjectAgreement, Checklist, ChecklistItem

def run():
    print "Uploading Country Admin data"


def getAllData():
    #get all the projects and loop over them
    getProjects = ProjectAgreement.objects.all()
    for item in getProjects:
            #if the project doesn't have a checklist create one
            try:
                get_checklist = Checklist.objects.get(agreement=item)
            except Checklist.DoesNotExist:
                get_checklist = Checklist(agreement=item)
                get_checklist.save()

                updateItems(get_checklist)
            #if it does update the items in the checklist to include all the new globals
            updateItems(get_checklist)
            print item

def updateItems(checklist):

    get_checklist = Checklist.objects.get(id=checklist.id)
    get_globals = ChecklistItem.objects.all().filter(global_item=True)
    for item in get_globals:
        look_for_existing = ChecklistItem.objects.all().filter(checklist=get_checklist, item=item)
        print item
        if look_for_existing:
            print "dupe do nothing"
        else:
            ChecklistItem.objects.create(checklist=get_checklist,item=item.item)
            print item

getAllData()