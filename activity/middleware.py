#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time


class TimingMiddleware(object):
    """
    Appends the X-PROCESSING_TIME_MS header to all responses.
    This value is the total time spent processing a user request
    in microseconds.
    """
    REQUEST_ATTR = '_timing_start'
    RESPONSE_HEADER = 'X-PROCESSING_TIME_MS'

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        # NOTE:- time.clock() is deprecated in python 3.8
        setattr(request, self.REQUEST_ATTR, time.perf_counter())

        response = self.get_response(request)
        # Code to be executed for each request/response after
        # the view is called.
        start = getattr(request, self.REQUEST_ATTR, None)
        if start:
            length = time.perf_counter() - start
            response[self.RESPONSE_HEADER] = "%i" % (length * 1000)

        return response
