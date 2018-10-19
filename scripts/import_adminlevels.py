"""
import json data from API
IMPORTANT!! you must turn off pagination for this to work from a URL and get all
country records
Install module django-extensions
Runs twice via function calls at bottom once
Syntax: sudo py manage.py runscript import_adminlevels
"""
from django.db import connection

cursor = connection.cursor()
import csv
from workflow.models import Country, Province, District, AdminLevelThree, Village

def run():
    print "Uploading Country Admin data"


def getAllData(getCountry,file_name):

    with open(file_name, 'rb') as csvfile:
        country = csv.reader(csvfile, delimiter=',', quotechar='"')
        print "PROVINCE (LEVEL 1) !!!!!!"
        #check for province and add new ones
        for row in country:
            column_num = 0
            for column in row:
                if column_num == 1:
                    print "Province="
                    print column
                    try:
                        Province.objects.get(name=column, country=getCountry)
                    except Province.DoesNotExist:
                        new_prov = Province(name=column, country=getCountry)
                        new_prov.save()
                    print column
                column_num = column_num + 1

    with open(file_name, 'rb') as csvfile2:
        country2 = csv.reader(csvfile2, delimiter=',', quotechar='"')
        #check for distrcit and add new one
        for row in country2:
            print "DISTRICTS (LEVEL 2) !!!!!!"
            column_num = 0
            for column in row:
                if column_num == 1:
                    getProvince = Province.objects.get(name=column, country=getCountry)

                if column_num == 2:
                    print "District="
                    print column

                    try:
                        District.objects.get(name=column, province=getProvince)
                    except District.DoesNotExist:
                        new_district = District(name=column, province=getProvince)
                        new_district.save()

                column_num = column_num + 1

    with open(file_name, 'rb') as csvfile2:
        country2 = csv.reader(csvfile2, delimiter=',', quotechar='"')
        #check for level3 and add new one
        for row in country2:
            print "LEVEL 3 !!!!!!"
            column_num = 0
            for column in row:
                if column_num == 1:
                    getProvince = Province.objects.get(name=column, country=getCountry)

                if column_num == 2:
                    getDistrict = District.objects.get(name=column, province=getProvince)

                if column_num == 3:
                    print "AdminLevelThree="
                    print column

                    try:
                        AdminLevelThree.objects.get(name=column, district=getDistrict)
                    except AdminLevelThree.DoesNotExist:
                        new_level_3 = AdminLevelThree(name=column, district=getDistrict)
                        new_level_3.save()

                column_num = column_num + 1

    with open(file_name, 'rb') as csvfile2:
        country2 = csv.reader(csvfile2, delimiter=',', quotechar='"')
        #check for village and add new one
        for row in country2:
            print "VILLAGE !!!!!"
            column_num = 0
            for column in row:
                if column_num == 1:
                    getProvince = Province.objects.get(name=column, country=getCountry)

                if column_num == 2:
                    getDistrict = District.objects.get(name=column, province=getProvince)

                if column_num == 3:
                    getAdminLevel3 = AdminLevelThree.objects.get(name=column, district=getDistrict)

                if column_num == 4:
                    print "Village="
                    print column

                    try:
                        Village.objects.get(name=column, admin_3=getAdminLevel3)
                    except Village.DoesNotExist:
                        new_level_3 = Village(name=column, admin_3=getAdminLevel3)
                        new_level_3.save()

                column_num = column_num + 1


# UNCOMMENT AND UPDATE TO IMPORT
print "IMPORTING South Sudan !!!!!!"
getCountry, created = Country.objects.get_or_create(country="Liberia")
file_name = "fixtures/Liberia_Admin.csv"
getAllData(getCountry, file_name)

"""
print "IMPORTING Uganda !!!!!!"
getCountry, created = Country.objects.get_or_create(country="Uganda")
file_name = "fixtures/admin-uganda.csv"
getAllData(getCountry, file_name)

"""
