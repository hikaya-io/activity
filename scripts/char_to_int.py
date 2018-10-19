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
from workflow.models import ProjectAgreement, ProjectComplete
import re

def run():
    print "Running Script..."

    trim_list = ['estimated_budget', 'actual_budget','total_cost','agency_cost','local_total_cost','local_agency_cost']

    #get all the projects and loop over them
    getProjects = ProjectComplete.objects.all()
    for item in getProjects:
        if item.total_cost and item.local_total_cost != "Nil":
            print item.total_cost
            trim_item = re.sub("[^0-9.]", "", item.total_cost)
            trim_item = float(trim_item)
            print trim_item
            ProjectComplete.objects.all().filter(id=item.id).update(total_cost=trim_item)
        elif item.total_cost in [None, '','Nil']:
            ProjectComplete.objects.all().filter(id=item.id).update(total_cost=0.00)

        if item.estimated_budget and item.local_total_cost != "Nil":
            print item.estimated_budget
            trim_item = re.sub("[^0-9.]", "", item.estimated_budget)
            trim_item = float(trim_item)
            print trim_item
            ProjectComplete.objects.all().filter(id=item.id).update(estimated_budget=trim_item)
        elif item.estimated_budget in [None, '','Nil']:
            ProjectComplete.objects.all().filter(id=item.id).update(estimated_budget=0.00)

        if item.agency_cost and item.local_total_cost != "Nil":
            print item.agency_cost
            trim_item = re.sub("[^0-9.]", "", item.agency_cost)
            trim_item = float(trim_item)
            print trim_item
            ProjectComplete.objects.all().filter(id=item.id).update(agency_cost=trim_item)
        elif item.agency_cost in [None, '','Nil']:
            ProjectComplete.objects.all().filter(id=item.id).update(agency_cost=0.00)

        if item.local_total_cost and item.local_total_cost != "Nil":
            print item.local_total_cost
            trim_item = re.sub("[^0-9.]", "", item.local_total_cost)
            trim_item = float(trim_item)
            print trim_item
            ProjectComplete.objects.all().filter(id=item.id).update(local_total_cost=trim_item)
        elif item.local_total_cost in [None, '','Nil']:
            ProjectComplete.objects.all().filter(id=item.id).update(local_total_cost=0.00)

        if item.local_agency_cost and item.local_agency_cost != "Nil":
            print item.local_agency_cost
            trim_item = re.sub("[^0-9.]", "", item.local_agency_cost)
            trim_item = float(trim_item)
            print trim_item
            ProjectComplete.objects.all().filter(id=item.id).update(local_agency_cost=trim_item)
        elif item.local_agency_cost in [None, '','Nil']:
            ProjectComplete.objects.all().filter(id=item.id).update(local_agency_cost=0.00)

    trim_list = ['total_estimated_budget', 'mc_estimated_budget','local_total_estimated_budget','local_mc_estimated_budget']

    #get all the projects and loop over them
    getProjectsComplete = ProjectAgreement.objects.all()
    for item in getProjectsComplete:
        if item.total_estimated_budget and item.total_estimated_budget != "Nil":
            print item.total_estimated_budget
            trim_item = re.sub("[^0-9.]", "", item.total_estimated_budget)
            trim_item = float(trim_item)
            print trim_item
            ProjectAgreement.objects.all().filter(id=item.id).update(total_estimated_budget=trim_item)
        elif item.total_estimated_budget in [None, '','Nil']:
            ProjectAgreement.objects.all().filter(id=item.id).update(total_estimated_budget=0.00)

        if item.mc_estimated_budget and item.mc_estimated_budget != "Nil":
            print item.mc_estimated_budget
            trim_item = re.sub("[^0-9.]", "", item.mc_estimated_budget)
            trim_item = float(trim_item)
            print trim_item
            ProjectAgreement.objects.all().filter(id=item.id).update(mc_estimated_budget=trim_item)
        elif item.mc_estimated_budget in [None, '','Nil']:
            ProjectAgreement.objects.all().filter(id=item.id).update(mc_estimated_budget=0.00)

        if item.local_total_estimated_budget and item.local_total_estimated_budget != "Nil":
            print item.local_total_estimated_budget
            trim_item = re.sub("[^0-9.]", "", item.local_total_estimated_budget)
            trim_item = float(trim_item)
            print trim_item
            ProjectAgreement.objects.all().filter(id=item.id).update(local_total_estimated_budget=trim_item)
        elif item.local_total_estimated_budget in [None, '','Nil']:
            ProjectAgreement.objects.all().filter(id=item.id).update(local_total_estimated_budget=0.00)

        if item.local_mc_estimated_budget and item.local_mc_estimated_budget != "Nil":
            print item.local_mc_estimated_budget
            trim_item = re.sub("[^0-9.]", "", item.local_mc_estimated_budget)
            trim_item = float(trim_item)
            print trim_item
            ProjectAgreement.objects.all().filter(id=item.id).update(local_mc_estimated_budget=trim_item)
        elif item.local_mc_estimated_budget in [None, '','Nil']:
            ProjectAgreement.objects.all().filter(id=item.id).update(local_mc_estimated_budget=0.00)