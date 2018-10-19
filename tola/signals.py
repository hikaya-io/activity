from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.conf import settings
from importlib import import_module

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore


@receiver(user_logged_in)
def sig_user_logged_in(sender, user, request, **kwargs):
    #get user profile data to set session vars
    #user_profile = UserProfile.objects.all().filter(user=request.user).values('country')
    #request.session['country'] = user_profile.country

    logger = logging.getLogger(__name__)
    logger.info("user logged in: %s at %s" % (user, request.META['REMOTE_ADDR']))

@receiver(user_logged_out)
def sig_user_logged_out(sender, user, request, **kwargs):
    logger = logging.getLogger(__name__)
    logger.info("user logged out: %s at %s" % (user, request.META['REMOTE_ADDR']))