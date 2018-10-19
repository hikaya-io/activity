from django.apps import apps
from django import db
from django.db import connection


app_models = apps.get_app_config('workflow').get_models()

#rename the app tables from the old activitydb to workflow
def run():

    print "Migration"

    for app in app_models:
        name = str(app._meta.db_table)
        new_appname = "tola_activity." + name
        temp = name.split("_")
        old_appname = "tola_activity.activitydb_" + temp[1]

        sql_query = "RENAME TABLE %s TO %s" % (old_appname,new_appname)

        print sql_query
        #catch any existing tables
        try:
            # Renaming model from 'Foo' to 'Bar'
            with connection.cursor() as cursor:
                cursor.execute(sql_query)
        except:
            "Table Already Exists"

        name_list = [
            'program_country',
            'program_fund_code',
            'program_sector',
            'program_user_access',
            'projectagreement_evaluate',
            'projectagreement_capacity',
            'projectagreement_stakeholder',
            'projectagreement_site',
            'projectcomplete_site',
            'projectcomplete_stakeholder',
            'quantitativeoutputs',
            'stakeholder_contact',
            'tolauser_countries'
            ]

        for name in name_list:
            old_appname = "tola_activity.activitydb_" + name
            new_appname = "tola_activity.workflow_" + name
            sql_query = "RENAME TABLE %s TO %s" % (old_appname, new_appname)
            try:
                # Renaming model from 'Foo' to 'Bar'
                with connection.cursor() as cursor:
                    cursor.execute(sql_query)
            except:
                "Table Already Exists"

        # rename formlibrary tables
        try:
            # Renaming model from 'Foo' to 'Bar'
            with connection.cursor() as cursor:
                cursor.execute("RENAME TABLE activitydb_beneficiary TO formlibrary_beneficiary")
                cursor.execute("RENAME TABLE activitydb_beneficiary_distribution TO formlibrary_beneficiary_distribution")
                cursor.execute("RENAME TABLE activitydb_beneficiary_program TO formlibrary_beneficiary_program")
                cursor.execute("RENAME TABLE activitydb_beneficiary_training TO formlibrary_beneficiary_training")
                cursor.execute("RENAME TABLE activitydb_trainingattendance TO formlibrary_trainingattendance")
                cursor.execute("RENAME TABLE activitydb_distribution TO formlibrary_distribution")
        except:
            "Table Already Exists"



