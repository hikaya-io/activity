#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":

    debug = os.environ.get('DEBUG', None)

    try:

        if debug is False and debug is not None:
            settings = 'activity.settings.production'

        elif 'test' in sys.argv:
            settings = 'activity.settings.test'

        else:
            settings = 'activity.settings.local'

    except ModuleNotFoundError:
        settings = 'activity.settings.local'

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
