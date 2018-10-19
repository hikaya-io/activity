"""
import json data from API
IMPORTANT!! you must turn off pagination for this to work from a URL and get all
country records
Install module django-extensions
Runs twice via function calls at bottom once
"""

from djangocosign.models import UserProfile, Country as CosignCountry
from workflow.models import TolaUser, Country


def run():
    print "Migrating User from Djangocosign to TolaUser"


def getAllData():
    getUsers = UserProfile.objects.all()
    for item in getUsers:
        cosign_user = UserProfile.objects.get(user=item.user)
        try:
            get_user = TolaUser.objects.get(user=item.user)
        except TolaUser.DoesNotExist:
            get_user = None
        print cosign_user.user
        try:
            get_country = Country.objects.get(code=cosign_user.country.iso_two_letters_code)
        except Country.DoesNotExist:
            get_country = None
        if get_user:
            print "user exists"
        else:
            get_user = TolaUser.objects.create(
            title=cosign_user.title,
            name=cosign_user.name,
            user=cosign_user.user,
            modified_by=cosign_user.modified_by,
            country=get_country
            )
            get_user.save()

getAllData()