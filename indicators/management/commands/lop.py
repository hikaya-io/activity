from django.core.management.base import BaseCommand, CommandError
from indicators.models import *
from django.utils import timezone

class Command(BaseCommand):
    help = """
        The script will look at each indicator and check to see if there are any data records associated with it.
        1. If NO, don't do anything further with this indicator.
        2. If YES, do the following:
            2.1. Set target frequency to "Life of Program only".
            2.2. Save this target frequency even if other required fields have errors or are incomplete.
            2.2. Assign all data records to the Life of Program target.'
        """

    def add_arguments(self, parser):
        parser.add_argument('--program_id', nargs='+', type=int)


    def handle(self, *args, **options):
        for option in options['program_id'] or []:
            self.stdout.write(self.style.SUCCESS('Process indicators for program_id = "%s"' % option))

        if options['program_id']:
            indicators = Indicator.objects.filter(program__in=options['program_id'])
        else:
            indicators = Indicator.objects.all() #filter(program = 452)

        for ind in indicators:
            collecteddata_count = ind.collecteddata_set.all().count()
            if collecteddata_count == 0:
                ind.periodictarget_set.all().delete()
                self.stdout.write(self.style.SUCCESS("%s, only deleted periodic_targets because data count is %s" % (ind.id, collecteddata_count)))
            else:
                try:
                    # disassociate collected_data records of this indicator with existing periodic targets
                    ind.collecteddata_set.update(periodic_target=None)

                    # remove all existing periodic targets
                    ind.periodictarget_set.all().delete()

                    # just checking to see if lop_target is a numeric value; if it is not then exception will be raised.
                    lop = float(ind.lop_target)

                    # create a "Life of Program (LOP) Only" target
                    lop_pt = PeriodicTarget.objects.create(\
                                indicator=ind,\
                                period=ind.TARGET_FREQUENCIES[0][1],\
                                target=ind.lop_target,\
                                create_date = timezone.now())

                    # associate all collected_data records of this indicator with the newly created "Life of Program (LOP) Only" target
                    ind.collecteddata_set.update(periodic_target=lop_pt)

                    # set the target_frequency of this indicator to "Life of Program (LOP) Only" target
                    ind.target_frequency = Indicator.LOP
                    ind.save()

                    self.stdout.write(self.style.SUCCESS('%s, Processed successfully.' % ind.id))
                except ValueError as e:
                    self.stdout.write(self.style.ERROR('%s, LOP [%s] is missing or not numeric.' % (ind.id, ind.lop_target)))
                except Exception as e:
                    self.stdout.write(self.style.ERROR("%s, Error occured: %s" % (ind.id, e)))

