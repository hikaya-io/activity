#!/usr/bin/python3
# -*- coding: utf-8 -*-

from functools import partial
from django import forms


class DatePicker(forms.DateInput):
    """
    Use in form to create a Jquery datepicker element
    """
    template_name = 'datepicker.html'
    DateInput = partial(forms.DateInput, {'class': 'datepicker'})
