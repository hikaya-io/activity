from django.contrib.auth.models import User,Group
from django.contrib.auth.hashers import make_password
from django.conf import settings
import datetime, ldap, re, logging
from workflow.models import Country, TolaUser

from django.utils.timezone import utc

logger = logging.getLogger("epro")

"""
******************************************************************************
Custom Backend Authentication to connect users against LDAP, instead of
the default django auth_user table.
******************************************************************************
"""
class RemoteUserBackend(object):

    """
    --------------------------------------------------------------------------------
    One of the two required methods for implementing custom backend authentication
    --------------------------------------------------------------------------------
    """
    def authenticate(self, username=None, password=None):
        if not username or not password:
            return False

        #user = None

        ldap_info = self.get_ldap_info('uid', username)
        if not ldap_info:
            logger.warning("Cannot get ldap info, user: %s" % username)
            return None
        
        is_authenticated = self.authenticate_user(username, password, ldap_info['email'], ldap_info['dn'])
        is_member = ldap_info['member']
        is_admin = ldap_info['admin']
        logger.error("is_authenticated %r    is_member: %r" % (is_authenticated, is_member))

        #if (is_authenticated is False or is_member is False):
        if (is_authenticated is False):
            logger.info("Unable to fetch user: %s" % username)
            return None

        user = self.create_or_sync_ldap_user(ldap_info, password)
        if user:
            self.update_userprofile(user, ldap_info)
            return user

        return None

    """
    --------------------------------------------------------------------------------
    Updates the user profile table (userprofile) with relevant info from the ldap_info
    --------------------------------------------------------------------------------
    """
    def update_userprofile(self, user, user_info):
        if not user_info:
            return False
        #logger.info("user_info (%s): " % user_info)
        
        create_params = {
            'created': datetime.datetime.utcnow().replace(tzinfo=utc), 
            'name': user_info['country_name']
            }
        country, new = Country.objects.get_or_create(
            iso_two_letters_code = user_info['country_id'],
            defaults=create_params)
        logger.info("New %r" % new)
        if new == True:
            country.save()
        
        create_params2 = {'created': datetime.datetime.utcnow().replace(tzinfo=utc), 'modified_by': user}
        userprofile, created = TolaUser.objects.get_or_create(
            user = user,
            defaults = create_params2)
        
        userprofile.country = country
        userprofile.name = user_info['full_name']
        userprofile.employee_number = user_info['employee_number']

        if created:
            logger.info("First time logging in")
        else:
            logger.info("Updating record for userprofile %s" % user_info['full_name'])

        userprofile.save()
        logger.info("Saved User Profile")
        return True


    """
    --------------------------------------------------------------------------------
    One of the two required methods for implementing custom backend authentication
    --------------------------------------------------------------------------------
    """
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    """
    --------------------------------------------------------------------------------
    When a user logs in to the api, this method checks if s/he has an account in ldap
    It creates an account in the auth_user table of the django if an account exist in
    ldap but not in the django app; otherwise, it updates it
    --------------------------------------------------------------------------------
    """
    def create_or_sync_ldap_user(self, ldap_info, password):

        # Check if the user exists, if not, create it.
        user, created = User.objects.get_or_create(username=ldap_info['uid'])
        if created:
            logger.info("AFTER: Created new user: %s created: %r" % (ldap_info['full_name'], created))
        else:
            logger.info("Existing user: %s created: %r" % (ldap_info['full_name'], created))

        user.first_name = ldap_info['first_name']
        user.last_name = ldap_info['last_name']
        user.email = ldap_info['email']

        # Password is stored locally also to enable redundancy.
        # In case LDAP is down, Django will fall back to local authentication.
        user.set_password(password)

        if not ldap_info['disabled']:
            user.is_active = True
        else:
            user.is_active = False

        # finally update the password to match the one in ldap
        user.password = make_password(password)
        if created:
            # add user to ViewOnly group by default
            user.groups.add(Group.objects.get(name='ViewOnly'))
        user.save()
        logger.info("Saved user: %s %s" % (user.first_name, user.last_name))
        return user

    """
    --------------------------------------------------------------------------------
    Authenticates the user against LDAP to make sure the credentials are correct
    --------------------------------------------------------------------------------
    """
    def authenticate_user(self, username=None, password=None, email=None, dn=None):

        # Get the email address only
        match = re.search('([\w.-]+)@([\w.-]+)', email)

        # Get the domain part from the email address
        domain = match.group(2)

        base_dn = ""
        for item in domain.split("."):
            base_dn += "DC=%s," % item

        # remove the trailing comma
        base_dn = base_dn[:-1]

        search_scope = ldap.SCOPE_SUBTREE

        # Do not require a certificate
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

        retrieve_attributes = ['uid','mail', 'givenName', 'uniqueId']
        search_filter = 'uid=' + username

        try:
            l = ldap.initialize(settings.LDAP_SERVER)
            l.simple_bind_s(dn, password)
        except ldap.SERVER_DOWN:
            logger.error("LDAP Server down!")
            return False
        except ldap.INVALID_CREDENTIALS:
            logger.warning("LDAP Invalid credentials supplied!")
            return False
        except ldap.LDAPError, e:
            logger.error("LDAP Error: %s - getting user info" % e)
            return False
        except Exception, e:
            logger.error("Exception: %s" % e)
            return False

        l.unbind()
        return True
    
    def get_ldap_country(self, dn):
        base_dn = 'DC=mercycorps,DC=org'
        search_scope = ldap.SCOPE_BASE
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        # http://stackoverflow.com/questions/4729539/how-do-i-search-for-an-object-in-ldap-based-on-its-dn-in-python-ldap
        country = None
        try:
            if bool(dn) == False:
                return country
            
            filter = dn.split(',')
            filter.pop(0)
            search_filter = ',' .join(filter)
            
            #search_filter = 'ou=People,dc=Portland,dc=us,dc=mercycorps,dc=org'
            
            #search_filter = '(&(ou=People)(|(objectClass=mercycorpsrealm)(objectClass=organizationalunit)))'
            l = ldap.initialize(settings.LDAP_SERVER)
            l.simple_bind_s(settings.LDAP_LOGIN, settings.LDAP_PASSWORD)
            #r = l.search_s(base_dn, search_scope, search_filter, retrieve_attributes)
            r = l.search_s(search_filter, search_scope, '(objectClass=*)')
            #for dn, entry in r:
            #    try:
            #        country = entry['description'][0])
            #    except KeyError:
            #        continue
            try:
                country = r[0][1]['description'][0]
            except Exception as e:
                logger.error(e)
                l.unbind()
                
        except ldap.LDAPError, e:
            logger.error("LDAP Error: %s - getting user info" % e)
            l.unbind()
        #l.unbind()
        return country
    """
    --------------------------------------------------------------------------------
    Connects to LDAP server and retrieves user info by looking up username
    --------------------------------------------------------------------------------
    """
    def get_ldap_info(self, attr, value):
        base_dn = 'DC=mercycorps,DC=org'
        search_scope = ldap.SCOPE_SUBTREE
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

        user_info = {}
        try:
            retrieve_attributes = ['uid', 'mail', 'employeeNumber', 'givenName', 'sn', 'cn', 'dn', 'nsAccountLock']
            search_filter = attr + '=' + value
            l = ldap.initialize(settings.LDAP_SERVER)
            l.simple_bind_s(settings.LDAP_LOGIN, settings.LDAP_PASSWORD)
            r = l.search_s(base_dn, search_scope, search_filter, retrieve_attributes)

            for dn, entry in r:
                if dn == None:
                    continue
                else:
                    user_info['dn'] = dn
                
                if entry.get('uid'):
                    user_info['uid'] = entry['uid'][0]
                else:
                    user_info['uid'] = ''

                m = re.match(r'^uid=\w+.*dc=(\w+),dc=mercycorps,dc=org$', dn)
                if m and len(m.group(1)) == 2:
                    user_info['country_id'] = m.group(1).upper()
                else:
                    user_info['country_id'] = 'XX'

                if entry.get('cn'):
                    user_info['full_name'] = entry['cn'][0]
                else:
                    user_info['full_name'] = ''

                if entry.get('sn'):
                    user_info['last_name'] = entry['sn'][0]
                else:
                    user_info['last_name'] = ''

                if entry.get('givenName'):
                    user_info['first_name'] = entry['givenName'][0]
                else:
                    user_info['first_name'] = ''

                if entry.get('mail'):
                    user_info['email'] = entry['mail'][0]
                else:
                    user_info['email'] = ''

                if entry.get('employeeNumber'):
                    user_info['employee_number'] = entry['employeeNumber'][0]
                else:
                    user_info['employee_number'] = ''

                if entry.get('nsAccountLock'):
                    user_info['disabled'] = True
                else:
                    user_info['disabled'] = False
                
                country = self.get_ldap_country(dn)
                if country is not None and bool(country) == True:
                    user_info['country_name'] = country
                
            # determine if user is a member of the 'mcapi' group
            retrieve_attributes = ['cn']

            # If user does not exist in LDAP, then do not bother checking for group membership
            if not user_info:
                return user_info

            # TODO: change the group name ertb to mcapi and then remove this comment
            search_filter = '(&(objectClass=mercycorpsGroup)(uniqueMember=uid='+user_info['uid']+',*)(cn=ertb))'
            r = l.search_s(base_dn, search_scope, search_filter, retrieve_attributes)

            if r:
                user_info['member'] = True
            else:
                user_info['member'] = False

            # Now determine if user is a member of the mcapi-admin group
            search_filter = '(&(objectClass=mercycorpsGroup)(uniqueMember=uid='+user_info['uid']+',*)(cn=ertb-admin))'
            r = l.search_s(base_dn, search_scope, search_filter, retrieve_attributes)

            if r:
                user_info['admin'] = True
            else:
                user_info['admin'] = False


        except ldap.LDAPError, e:
            logger.error("LDAP Error: %s - getting user info" % e)

        l.unbind()
        return user_info
