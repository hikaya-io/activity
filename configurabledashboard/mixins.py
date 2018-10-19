from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from rest_framework import authentication, permissions, viewsets

class LoggedInMixin(object):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixin, self).dispatch(*args, **kwargs)


class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response

#API Mixin
class APIDefaultsMixin(object):   
    """Default settings for view authentication, permissions,   
     filtering and pagination."""   

    authentication_classes = (
         authentication.BasicAuthentication,        
         authentication.TokenAuthentication,
    )   
    permission_classes = (
         permissions.IsAuthenticated,
    )   
    paginate_by = 20    
    paginate_by_param = 'page_size'    
    max_paginate_by = 50