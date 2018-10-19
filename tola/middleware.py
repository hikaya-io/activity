import time

class TimingMiddleware(object):
    """
    Appends the X-PROCESSING_TIME_MS header to all responses.
    This value is the total time spent processing a user request in microseconds.
    """
    REQUEST_ATTR = '_timing_start'
    RESPONSE_HEADER = 'X-PROCESSING_TIME_MS'

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.


    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        setattr(request, self.REQUEST_ATTR, time.clock())

        response = self.get_response(request)
        # Code to be executed for each request/response after
        # the view is called.
        start = getattr(request, self.REQUEST_ATTR, None)
        if start:
            length = time.clock() - start
            response[self.RESPONSE_HEADER] = "%i" % (length * 1000)

        return response
