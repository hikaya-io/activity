#!/usr/bin/python3
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.utils import timezone

import dateutil.parser
import csv
from time import strptime
from datetime import datetime

from indicators.models import (Indicator, PeriodicTarget, CollectedData, )
from indicators.views import generate_periodic_targets


class Command(BaseCommand):
    help = """
        Setup targets for indicators by reading a CSV file
        """

    def add_arguments(self, parser):
        """
        Help on arguments: https://docs.python.org/3/library/argparse.html
                                #argparse.ArgumentParser.add_argument
        """
        parser.add_argument('-f', '--file', action='store',
                            nargs='?', required=True, dest='filepath')

    def handle(self, *args, **options):
        file = options['filepath']
        self.stdout.write(self.style.WARNING(
            'creating targetes for indicators from = "%s"' % file))

        with open(file, 'rb') as csvfile:
            indicatorcsv_reader = csv.reader(csvfile)
            # This skips the first row (header) of the CSV file.
            next(indicatorcsv_reader)

            for row in indicatorcsv_reader:
                indicator_id = row[0].strip()
                target_frequency = row[4].strip()
                month_name = row[5].strip()
                year = row[6].strip()
                num_targets = row[7].strip()
                target_frequency_start = None

                # lookup target_frequency index:
                target_frequency_id = next((i for i, v in enumerate(
                    Indicator.TARGET_FREQUENCIES) if v[1] == target_frequency),
                                           None)
                if target_frequency_id is None:
                    self.stdout.write(self.style.ERROR(
                        '%s, invalid target_frequency = %s' %
                        (indicator_id, target_frequency)))
                    continue
                else:
                    target_frequency_id += 1

                # make sure month is valid
                try:
                    month = strptime(month_name, '%B').tm_mon
                except ValueError:
                    self.stdout.write(self.style.ERROR(
                        '%s, invalid month = %s' % (indicator_id, month_name)))
                    continue

                # make sure year is valid
                try:
                    year = float(year) if '.' in year else int(year)
                except ValueError:
                    self.stdout.write(self.style.ERROR(
                        '%s, invalid year = %s' % (indicator_id, year)))
                    continue

                # make sure num_targets is valid
                try:
                    num_targets = float(
                        num_targets) if '.' in num_targets \
                        else int(num_targets)
                except ValueError:
                    self.stdout.write(self.style.ERROR(
                        '%s, invalid num_targets = %s' %
                        (indicator_id, num_targets)))
                    continue

                # Fetch the indicator
                try:
                    indicator = Indicator.objects.get(pk=indicator_id)
                except Indicator.DoesNotExist:
                    self.stdout.write(self.style.ERROR(
                        '%s, indicator does not exist!' % indicator_id))
                    continue

                try:
                    target_frequency_start = datetime.strptime(
                        '%s-%s-%s' % (year, month, '01'), '%Y-%m-%d')
                except ValueError:
                    self.stdout.write(self.style.ERROR(
                        '%s, %s target_frequency_start date parse error' %
                        (indicator_id, target_frequency_start)))
                    continue

                generated_targets = generate_periodic_targets(
                    target_frequency_id, target_frequency_start, num_targets,
                    None)

                for i, pt in enumerate(generated_targets):
                    try:
                        start_date = dateutil.parser.parse(
                            pt.get('start_date', None))
                        start_date = datetime.strftime(start_date, '%Y-%m-%d')
                    except (ValueError, AttributeError):
                        start_date = None

                    try:
                        end_date = dateutil.parser.parse(
                            pt.get('end_date', None))
                        end_date = datetime.strftime(end_date, '%Y-%m-%d')
                    except (ValueError, AttributeError):
                        end_date = None

                    if target_frequency_id == Indicator.LOP:
                        period = Indicator.TARGET_FREQUENCIES[0][1]
                    else:
                        try:
                            period = pt.get('period', None)
                        except AttributeError:
                            self.stdout.write(self.style.ERROR(
                                '%s, --- no period' % indicator.id))
                            continue

                    if target_frequency_id == Indicator.LOP:
                        target_value = indicator.lop_target
                    else:
                        try:
                            target_value = pt.get('target', '0')
                        except AttributeError:
                            self.stdout.write(self.style.ERROR(
                                '%s, --- there is no target for this '
                                'period (%s)' % (indicator.id, period)))

                    try:
                        target = float(target_value) if '.' in target_value \
                            else int(target_value)
                    except ValueError:
                        self.stdout.write(self.style.ERROR(
                            '%s, --- target is not a numeric value (%s)' %
                            (indicator.id, target_value)))
                        continue

                    try:
                        ptarget = PeriodicTarget.objects.create(
                            indicator=indicator,
                            period=period,
                            target=target,
                            customsort=i,
                            start_date=start_date,
                            end_date=end_date,
                            create_date=timezone.now())
                    except Exception:
                        self.stdout.write(self.style.ERROR(
                            '%s, --- could not create target (%s)' %
                            (indicator.id, period)))
                        continue

                    try:
                        CollectedData.objects.filter(
                            indicator=indicator,
                            date_collected__range=[ptarget.start_date, ptarget.end_date])\
                            .update(periodic_target=ptarget)
                    except Exception:
                        self.stdout.write(self.style.ERROR(
                            '%s, could not associate data records for '
                            'periodic_target (%s)' %
                            (indicator.id, ptarget.period)))

                try:
                    indicator.target_frequency = target_frequency_id
                    if target_frequency_id != Indicator.LOP:
                        indicator.target_frequency_start = \
                            target_frequency_start
                        indicator.target_frequency_num_periods = num_targets
                    indicator.save()
                    self.stdout.write(self.style.SUCCESS(
                        '%s, processed successfully.' % indicator.id))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        '%s, failed to save indicator: %s' %
                        (indicator.id, e)))
