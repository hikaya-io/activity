from django.contrib.auth.models import User,Permission, Group
from django.conf import settings
import datetime, ldap, re, logging
from workflow.models import TolaUser, Country

from django.contrib.auth.backends import RemoteUserBackend
from django.utils.timezone import utc

logger = logging.getLogger("tola")


class CosignBackend(RemoteUserBackend):
    """
    In addition to Authentication backend for Cosign/SSO, it retrieves
    additional info from LDAP to populate the fields such as email,
    full name, and fields in the profile/userprofile table such as employee_number,etc.
    """
    def clean_username(self, username):
        #logger.error("username is claned.....")
        """
        Performs any cleaning on the "username" prior to using it to get or
        create the user object.  Returns the cleaned username.

        By default, returns the username unchanged.
        """

        try:
            user = User.objects.get(username__exact=username)
            self.configure_user(user)
        except Exception as e:
            pass

        return username

    def configure_user(self, user):
        """
        Configures a user after creation and returns the updated user.

        By default, returns the user unmodified.
        """
        username = str(user.username)

        ldap_info = self.get_ldap_info(str('uid'), username)

        if not ldap_info:
            logger.error("Could not retrieve info for %s in ldap" % user.username)
            return user

        user.first_name = ldap_info['first_name']
        user.last_name = ldap_info['last_name']
        user.email = ldap_info['email']

        user.save()

        # Now update extended user profile table with employee_number, etc.
        self.update_userprofile(user, ldap_info)

        return user

    def update_userprofile(self, user, ldap_info):
        """
        Creates or updates a relevant entry for a user in their profile/userprofile
        table

        This is needed because the user table does not have fields for employee_number,
        etc.
        """
        create_params = {
            'create_date': datetime.datetime.utcnow().replace(tzinfo=utc),
            'country': ldap_info['country_name']
            }
        country, new = Country.objects.get_or_create(
            code = ldap_info['country_id'],
            defaults = create_params)
        if new == True:
            country.save()

        userprofile, created = TolaUser.objects.get_or_create(
            user = user)

        userprofile.country = country

        userprofile.name = ldap_info['full_name']
        userprofile.employee_number = ldap_info['employee_number']

        userprofile.save()
        #add user to country permissions table
        userprofile.countries.add(country)

        return True

    def get_ldap_country(self, dn):
        """
        Retrieve the country associated with a user

        This is used to assign the user to the appropriate country
        """
        base_dn = 'DC=mercycorps,DC=org'
        search_scope = ldap.SCOPE_BASE
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        country = None
        try:
            if bool(dn) == False:
                return country
            filter = dn.split(',')
            filter.pop(0)
            search_filter = ',' . join(filter)
            l = ldap.initialize(settings.LDAP_SERVER)
            l.simple_bind_s(settings.LDAP_LOGIN, settings.LDAP_PASSWORD)
            r = l.search_s(search_filter, search_scope, '(objectClass=*)')
            try:
                country = r[0][1]['description'][0]
            except Exception as e:
                logger.error("Error getting country: %s" % e)
                l.unbind()
        except ldap.LDAPError, e:
            logger.error("LDAP Error: %s - while getting country info" % e)
        except Exception as e:
            logger.error("LDAP Error: %s - while getting country info" % e)
        l.unbind()
        return country

    def get_ldap_info(self, attr, value):
        """
        Retrieve additional information from LDAP based on the remote_user passed-in by
        cosign

        """
        base_dn = 'DC=mercycorps,DC=org'
        search_scope = ldap.SCOPE_SUBTREE
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

        ldap_info = {}
        try:
            attributes = [str('uid'), str('mail'), str('employeeNumber'), str('givenName'),
            str('sn'), str('cn'), str('dn'), str('nsAccountLock')]
            search_filter = str(attr + '=' + value)
            l = ldap.initialize(settings.LDAP_SERVER)
            l.simple_bind_s(settings.LDAP_LOGIN, settings.LDAP_PASSWORD)
            r = l.search_s(base_dn, search_scope, search_filter, attributes)
            for dn, entry in r:
                if dn == None:
                    continue
                else:
                    ldap_info['dn'] = dn

                if entry.get('uid'):
                    ldap_info['uid'] = entry['uid'][0]
                else:
                    ldap_info['uid'] = ''

                m = re.match(r'^uid=\w+.*dc=(\w+),dc=mercycorps,dc=org$', dn)
                if m and len(m.group(1)) == 2:
                    ldap_info['country_id'] = m.group(1).upper()
                else:
                    ldap_info['country_id'] = 'XX'

                if entry.get('cn'):
                    ldap_info['full_name'] = entry['cn'][0]
                else:
                    ldap_info['full_name'] = ''

                if entry.get('sn'):
                    ldap_info['last_name'] = entry['sn'][0]
                else:
                    ldap_info['last_name'] = ''

                if entry.get('givenName'):
                    ldap_info['first_name'] = entry['givenName'][0]
                else:
                    ldap_info['first_name'] = ''

                if entry.get('mail'):
                    ldap_info['email'] = entry['mail'][0]
                else:
                    ldap_info['email'] = ''

                if entry.get('employeeNumber'):
                    ldap_info['employee_number'] = entry['employeeNumber'][0]
                else:
                    ldap_info['employee_number'] = ''

                if entry.get('nsAccountLock'):
                    ldap_info['disabled'] = True
                else:
                    ldap_info['disabled'] = False

                country = self.get_ldap_country(dn)
                if country is not None and bool(country) == True:
                    ldap_info['country_name'] = country

            attributes = [str('cn')]

            # TODO: change the group name ertb to mcapi and then remove this comment
            search_filter = '(&(objectClass=mercycorpsGroup)(uniqueMember=uid='+ldap_info['uid']+',*)(cn=ertb))'
            r = l.search_s(base_dn, search_scope, search_filter, attributes)

            if r:
                ldap_info['member'] = True
            else:
                ldap_info['member'] = False

            # TODO: change the group name ertb to mcapi and then remove this comment
            # Now determine if user is a member of the mcapi-admin group
            search_filter = '(&(objectClass=mercycorpsGroup)(uniqueMember=uid='+ldap_info['uid']+',*)(cn=ertb-admin))'
            r = l.search_s(base_dn, search_scope, search_filter, attributes)

            if r:
                ldap_info['admin'] = True
            else:
                ldap_info['admin'] = False

        except Exception as e:
            logger.error("Error: %s %s- while getting user info" % (type(e), e))
        l.unbind()
        return ldap_info
