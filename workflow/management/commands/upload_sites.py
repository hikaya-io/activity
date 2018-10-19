import csv
import re
from django.core.management.base import BaseCommand, CommandError
from workflow.models import *
from django.utils import timezone

class Command(BaseCommand):
    help = """
        Uploads sites from a CSV file
        usage: sudo py -W ignore  manage.py upload_sites -f ~/country_data.csv
        """

    def add_arguments(self, parser):
        """
        Help on arguments: https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_argument
        """
        parser.add_argument('-f', '--file', action='store', nargs='?', required=True, dest='filepath')


    def handle(self, *args, **options):
        file = options['filepath']
        self.stdout.write(self.style.WARNING('reading sites from: "%s"' % file))

        with open(file, 'rb') as csvfile:
            sites_reader = csv.reader(csvfile)
            # This skips the first row (header) of the CSV file.
            next(sites_reader)

            for row in sites_reader:
                site_name = row[0].strip()
                type_of_site = row[1].strip()
                # read the first 7 characters only
                # latitude = re.sub('[^0-9]', '', row[2])
                latitude = re.findall('\d+\.\d+', row[2])
                longitude = re.findall('\d+\.\d+', row[3])
                office_name = row[4].strip()
                contact = row[5].strip()
                country_name = row[6].strip()
                province_name = row[7].strip()
                district_name = row[8].strip()

                try:
                    latitude = latitude[0]
                except IndexError:
                    latitude = None

                try:
                    longitude = longitude[0]
                except IndexError:
                    longitude = None

                try:
                    country = Country.objects.get(country=country_name)
                except Country.DoesNotExist:
                    self.stdout.write(self.style.ERROR('%s, country not found (%s)' % (site_name, country_name) ))
                    continue

                try:
                    provinces = Province.objects.filter(country=country)
                    office = Office.objects.get(name=office_name, province__in=provinces)
                except Office.DoesNotExist:
                    self.stdout.write(self.style.WARNING('%s, invalid office_name = %s' % (site_name, office_name) ))
                    office = None
                except Office.MultipleObjectsReturned:
                    self.stdout.write(self.style.WARNING('%s, multiple offices with the same name = %s' % (site_name, office_name) ))
                    office = None

                try:
                    profile_type = ProfileType.objects.get(profile=type_of_site)
                except ProfileType.DoesNotExist:
                    profile_type = None

                try:
                    province = Province.objects.get(name=province_name)
                except Province.DoesNotExist:
                    self.stdout.write(self.style.ERROR('%s, province not found (%s)' % (site_name, province_name) ))
                    continue

                try:
                    district = District.objects.get(name=district_name)
                except District.DoesNotExist:
                    self.stdout.write(self.style.ERROR('%s, district not found (%s)' % (site_name, district_name) ))
                    continue

                try:
                    lat = float(latitude)
                except ValueError as e:
                    lat = None
                    self.stdout.write(self.style.WARNING('%s, invalid latitude = %s' % (site_name, latitude) ))

                try:
                    lon = float(longitude)
                except ValueError as e:
                    lon = None
                    self.stdout.write(self.style.WARNING('%s, invalid longitude = %s' % (site_name, longitude) ))

                try:
                    site, created = SiteProfile.objects.update_or_create(name = site_name,\
                        defaults = {\
                            'type': profile_type, 'office': office, 'contact_leader': contact,\
                            'latitude': lat, 'longitude': lon, 'country': country, 'province': province,\
                            'district': district, 'create_date': timezone.now()\
                            })
                    self.stdout.write(self.style.SUCCESS('%s site_profile created(%s) successfully!' % (site_name, created)))
                except Exception as e:
                    self.stdout.write(self.style.ERROR('%s, could not update or create site_profile %s ' % (site_name, e) ))
                    continue