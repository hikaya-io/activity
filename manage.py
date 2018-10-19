#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":

    settings = 'tola.settings.test' if 'test' in sys.argv else 'tola.settings.local'

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
