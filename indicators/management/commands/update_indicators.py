import csv
from django.core.management.base import BaseCommand, CommandError
from indicators.models import *
from django.utils import timezone

class Command(BaseCommand):
    help = """
        Update lop, unit_of_measure, and baseline values of indicators based on a csv file
        usage: sudo py -W ignore  manage.py update_indicators -f ~/country_data.csv
        """

    def add_arguments(self, parser):
        """
        Help on arguments: https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_argument
        """
        parser.add_argument('-f', '--file', action='store', nargs='?', required=True, dest='filepath')


    def handle(self, *args, **options):
        file = options['filepath']
        self.stdout.write(self.style.WARNING('reading indicators info from: "%s"' % file))

        with open(file, 'rb') as csvfile:
            indicatorcsv_reader = csv.reader(csvfile)
            # This skips the first row (header) of the CSV file.
            next(indicatorcsv_reader)
            for row in indicatorcsv_reader:
                indicator_id = row[0]
                unit_of_measure = row[4]
                lop = row[5].replace(',', '')
                baseline = row[6].replace(',', '')
                baseline_na = False
                indicator = None
                try:
                    lop = float(lop) if '.' in lop else int(lop)
                except ValueError as e:
                    self.stdout.write(self.style.ERROR('%s, invalid lop (%s)' % (indicator_id, lop) ))
                    continue

                try:
                    baseline = float(baseline) if '.' in baseline else int(baseline)
                except ValueError as e:
                    if baseline and baseline.lower() == 'na' or baseline.lower() == 'n/a' or baseline.lower() == 'not applicable':
                        baseline_na = True
                    else:
                        self.stdout.write(self.style.ERROR('%s, invalid baseline (%s)' % (indicator_id, baseline) ))
                        continue

                try:
                    indicator = Indicator.objects.get(pk=indicator_id)
                except Indicator.DoesNotExist as e:
                    self.stdout.write(self.style.ERROR('%s, does not exist!' % indicator_id))
                    continue

                try:
                    indicator.unit_of_measure = unit_of_measure
                    indicator.lop_target = lop
                    if baseline_na == True:
                        indicator.baseline = None
                        indicator.baseline_na = True
                    else:
                        indicator.baseline = baseline
                    indicator.save()
                    self.stdout.write(self.style.SUCCESS("%s, updated successfully" % indicator.id))
                except Exception as e:
                    self.stdout.write(self.style.ERROR('%s, failed to save!' % indicator.id))

