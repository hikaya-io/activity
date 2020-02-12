#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":

    debug = os.environ.get('DEBUG', None)
    settings = 'Activity.settings.local'
    try:

        if debug is False and debug is not None:
            settings = 'Activity.settings.production'

        elif 'test' in sys.argv:
            settings = 'Activity.settings.test'

        else:
            settings = 'Activity.settings.local'

    except ModuleNotFoundError:
        settings = 'Activity.settings.local'

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
