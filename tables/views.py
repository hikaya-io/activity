#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render
from indicators.models import ActivityTable, ExternalService

import json
import requests


def home(request):
    """
    Import
    """
    return render(request, 'tables/home.html')


def import_table(request):
    """
    import collected data from Activity Tables
    """
    owner = request.user
    service = ExternalService.objects.get(name="activitytables")

    # add filter to get just the users tables only
    user_filter_url = service.feed_url + "&owner__username=" + str(owner)
    # public_filter_url = service.feed_url + "&public=True"
    # shared_filter_url = service.feed_url + "&shared__username=" + str(owner)

    response = requests.get(user_filter_url)
    user_json = json.loads(response.content)

    data = user_json

    # debug the json data string uncomment dump and print
    # data2 = json.dumps(data) # json formatted string
    # print data2

    if request.method == 'POST':
        id = request.POST['service_table']
        filter_url = service.feed_url + "&id=" + id
        response = requests.get(filter_url)
        get_json = json.loads(response.content)
        data = get_json
        for item in data['results']:
            name = item['name']
            url = item['data']
            remote_owner = item['owner']['username']

        check_for_existence = ActivityTable.objects.all()\
            .filter(name=name, owner=owner)
        if check_for_existence:
            message = "error"
        else:
            create_table = ActivityTable.objects.create(
                name=name, owner=owner, remote_owner=remote_owner,
                table_id=id, url=url)
            create_table.save()
            message = "success"

        # send result back as json
        return HttpResponse(json.dumps(message),
                            content_type='application/json')

    # send the keys and vars from the json data to the template along with
    # submitted feed info and silos for new form
    return render(request, "tables/import.html", {'getTables': data})
