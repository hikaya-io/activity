djangocosign
============

This is an app that provides an "Authentication Backend" to a Django powered site. There are two files in this 
app.

The first file is ldapauth.py, which inhertis from Ojbect. This is a custom implementation to provide a RemoteUserBackend unlike the second implementation, which inherits from RemoteUserBackend class and overrides certain methods.
The second file named cosign.py inherits from RemoteUserBackend, which is a class in django.contrib.auth.backends.

The ldapauth.py is kept mostly for reference purposes. It is recommended to use the cosign.py implementation.

Both files provide LDAP based authentication RemoteUserBackend authentication mechanism to a Django Powered site.

### requires: ###
* python-ldap (pip install python-ldap)

### Installation: ###
* add 'djangocosign' to your INSTALLED_APPS
```
    INSTALLED_APPS = (
        ...,
        'djangocosign',
        ...,
    )
```

### Specify Authentication Backend in your settings file: ###
```
    AUTHENTICATION_BACKENDS = (
        'ldaplogin.cosign.CosignBackend',
        'django.contrib.auth.backends.ModelBackend',
    )
```
