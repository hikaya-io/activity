from activity import views
from activity.views import (
    BookmarkList, BookmarkCreate, BookmarkDelete, BookmarkUpdate,
    UserInviteView, PasswordReset,
)
from feed.views import (
    UserViewSet, ProgramViewSet, SectorViewSet, ProjectTypeViewSet,
    OfficeViewSet, SiteProfileViewSet, CountryViewSet,
    AgreementViewSet, CompleteViewSet, PeriodicTargetReadOnlyViewSet,
    ObjectiveViewSet, OrganizationViewSet, LoggedUserViewSet,
    PogramIndicatorReadOnlyViewSet, ProjectAgreementViewSet, ChecklistViewSet,
    CollectedDataViewSet, IndicatorViewSet, ReportingFrequencyViewSet,
    ExternalServiceRecordViewSet, DisaggregationValueViewSet, EvaluateViewSet,
    CapacityViewSet, ActivityUserViewSet, ProfileTypeViewSet, DistrictViewSet,
    DocumentationViewSet, IndicatorTypeViewSet, StakeholderTypeViewSet, ContactViewSet,
    ActivitytableViewSet, VillageViewSet, StrategicObjectiveViewSet, ProvinceViewSet,
    AdminLevelThreeViewSet, ExternalServiceViewSet, DisaggregationTypeViewSet,
    LevelViewSet, StakeholderViewSet
)
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken import views as auth_views
from django.contrib.auth import views as authviews
from django.shortcuts import redirect
from activity import views as activityviews

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
admin.site.site_header = 'Activity Settings'
admin.site.site_title = 'Activity Settings Page'
admin.site.index_title = 'Welcome to Activity Settings'

# REST FRAMEWORK
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'programs', ProgramViewSet)
router.register(r'sector', SectorViewSet)
router.register(r'projecttype', ProjectTypeViewSet)
router.register(r'office', OfficeViewSet)
router.register(r'siteprofile', SiteProfileViewSet)
router.register(r'country', CountryViewSet)
router.register(r'initiations', AgreementViewSet)
router.register(r'tracking', CompleteViewSet)
router.register(r'indicator', IndicatorViewSet)
router.register(r'reportingfrequency', ReportingFrequencyViewSet)
router.register(r'activityuser', ActivityUserViewSet)
router.register(r'indicatortype', IndicatorTypeViewSet)
router.register(r'objective', ObjectiveViewSet)
router.register(r'disaggregationtype', DisaggregationTypeViewSet)
router.register(r'level', LevelViewSet)
router.register(r'externalservice', ExternalServiceViewSet)
router.register(r'externalservicerecord', ExternalServiceRecordViewSet)
router.register(r'strategicobjective', StrategicObjectiveViewSet)
router.register(r'stakeholder', StakeholderViewSet)
router.register(r'stakeholdertype', StakeholderTypeViewSet)
router.register(r'capacity', CapacityViewSet)
router.register(r'evaluate', EvaluateViewSet)
router.register(r'profiletype', ProfileTypeViewSet)
router.register(r'province', ProvinceViewSet)
router.register(r'district', DistrictViewSet)
router.register(r'adminlevelthree', AdminLevelThreeViewSet)
router.register(r'village', VillageViewSet)
router.register(r'contact', ContactViewSet)
router.register(r'documentation', DocumentationViewSet)
router.register(r'collecteddata', CollectedDataViewSet)
router.register(r'activitytable', ActivitytableViewSet,
                basename='activitytable')
router.register(r'disaggregationvalue', DisaggregationValueViewSet)
router.register(r'projectagreements', ProjectAgreementViewSet)
router.register(r'loggedusers', LoggedUserViewSet)
router.register(r'checklist', ChecklistViewSet)
router.register(r'organization', OrganizationViewSet)
router.register(r'pindicators', PogramIndicatorReadOnlyViewSet,
                basename='pindicators')
router.register(r'periodictargets', PeriodicTargetReadOnlyViewSet,
                basename='periodictargets')


urlpatterns = [  # rest framework
    path('select2/', include('django_select2.urls')),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls',
                              namespace='rest_framework')),
    path('api-token-auth/', auth_views.obtain_auth_token),

    # index
    path('', lambda request: redirect('dashboard/0/', permanent=False), name="index"),

    # enable the admin:
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('<slug:selected_countries>/', views.IndexView.as_view(), name='index'),

    # index
    path('dashboard/<int:program_id>/',
         activityviews.IndexView.as_view(), name='home_dashboard'),

    # base template for layout
    path('', TemplateView.as_view(template_name='base.html')),

    # enable admin documentation:
    path('admin/doc/', include('django.contrib.admindocs.urls')),

    # app include of workflow urls
    path('workflow/', include('workflow.urls')),

    # app include of indicator urls
    path('indicators/', include('indicators.urls')),

    # app include of customdashboard urls
    path('customdashboard/', include('customdashboard.urls')),

    # app include of reports urls
    path('reports/', include('reports.urls')),

    # app include of workflow urls
    path('formlibrary/', include('formlibrary.urls')),
    # local login
    path('login/', authviews.LoginView.as_view(), name='login'),
    path('accounts/login/', views.UserLogin.as_view(), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/logout/', views.logout_view, name='logout'),
    # register
    path('accounts/register/user/<slug:invite_uuid>/', views.register, name='register'),
    path('accounts/join/organization/<slug:invite_uuid>/', views.invite_existing_user,
         name='join_organization'),
    path('accounts/register/organization', views.RegisterOrganization.as_view(),
         name='register_organization'),

    # password reset
    path('accounts/user/password_reset/', PasswordReset.as_view(is_admin_site=True),
         {'is_admin_site': 'True'}, name='user_password_reset'),
    path('accounts/user/password_update/', views.change_password, name='change_password'),

    # accounts
    path('accounts/organization/<int:org_id>/',
         views.switch_organization, name='switch_organization'),
    path('accounts/profile/', views.profile, name='profile'),
    path('accounts/admin_dashboard/', views.admin_dashboard,
         name='admin_dashboard'),
    path('accounts/admin/users/<slug:role>/<slug:status>/', views.admin_user_management,
         name='admin_user_management'),
    path('accounts/admin/user/edit/<int:pk>/', views.admin_user_edit,
         name='admin_user_edit'),
    path('accounts/admin/user/updatestatus/<int:pk>/<slug:status>/', views.update_user_access,
         name='user_status_update'),
    path('accounts/admin/configurations', views.admin_configurations,
         name='admin_configurations'),
    path('accounts/admin/profile_settings', views.admin_profile_settings,
         name='admin_profile_settings'),
    path('accounts/admin/invite_user/', views.invite_user,
         name='invite_user'),
    path('accounts/admin/users/invitations/list/<slug:organization>/', views.admin_user_invitations,
         name='admin_user_invitations'),
    path('accounts/admin/invitations/', UserInviteView.as_view(), name='user_invitations'),
    path('accounts/admin/workflow_settings', views.admin_workflow_settings,
         name="admin_workflow_settings"),
    path('accounts/admin/indicator_settings', views.admin_indicator_settings,
         name="admin_indicator_settings"),
    path('accounts/admin/form_library_settings', views.admin_form_library_settings,
         name="admin_form_library_settings"),
    path('accounts/admin/component_admin', views.admin_component_admin,
         name="admin_component_admin"),
    path(
        'accounts/admin/indicator_configs_admin',
        views.admin_indicator_config,
        name='indicator_configs_admin'
    ),
    path(
        'accounts/admin/map_settings',
        views.admin_map_settings,
        name='admin_map_settings'
    ),

    # bookmarks
    path('bookmark_list', BookmarkList.as_view(),
         name='bookmark_list'),
    path('bookmark_add', BookmarkCreate.as_view(), name='bookmark_add'),
    path('bookmark_update/<int:pk>/',
         BookmarkUpdate.as_view(), name='bookmark_update'),
    path('bookmark_delete/<int:pk>/',
         BookmarkDelete.as_view(), name='bookmark_delete'),

    # Auth backend URL's
    path('', include(('django.contrib.auth.urls',
                      "django.contrib.auth"), namespace='auth')),
    path('activate/<slug:uidb64>/<slug:token>/',
         views.activate_acccount, name='activate'),
    path('oauth/',
         include('social_django.urls', namespace='social')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

        # For django versions before 2.0:
        # url(r'^__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns
