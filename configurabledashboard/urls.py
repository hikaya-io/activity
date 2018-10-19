from .views import *

from django.conf.urls import *

# place app url patterns here

urlpatterns = [

                       url(r'^(?P<pk>[0-9]+)/$', CustomDashboardList.as_view(), name='custom_dashboard_list'),
                       url(r'^detail/(?P<pk>[0-9]+)/$', CustomDashboardDetail.as_view(), name='custom_dashboard_detail'),
                       url(r'^add/(?P<pk>[0-9]+)/$', CustomDashboardCreate.as_view(), name='custom_dashboard_add'),
                       url(r'^update/(?P<pk>[0-9]+)/$', CustomDashboardUpdate.as_view(template_name="configurabledashboard/dashboard/form.html"), name='custom_dashboard_update'),
                       url(r'^edit/(?P<pk>[0-9]+)/$', CustomDashboardUpdate.as_view(template_name="configurabledashboard/dashboard/modal_form.html"), name='custom_dashboard_edit'),
                       url(r'^map/(?P<pk>[0-9]+)/(?P<location>[0-9]+)/(?P<type>[-\w]+)/$', custom_dashboard_update_components, name='custom_dashboard_update_components'),
                       url(r'^remap/(?P<pk>[0-9]+)/(?P<location>[0-9]+)/(?P<type>[-\w]+)/$', CustomDashboardUpdate.as_view(template_name="configurabledashboard/components/admin/remap.html"), name='custom_dashboard_unmap'),
                       url(r'^delete/(?P<pk>[0-9]+)/$', CustomDashboardDelete.as_view(), name='custom_dashboard_delete'),

                       url(r'^theme/$', DashboardThemeList.as_view(), name='dashboard_theme_list'),
                       url(r'^theme_add/$', DashboardThemeCreate.as_view(), name='dashboard_theme_add'),
                       url(r'^theme_update/(?P<pk>[0-9]+)/$', DashboardThemeUpdate.as_view(), name='custom_dashboard/theme_update'),
                       url(r'^theme_delete/(?P<pk>[0-9]+)/$', DashboardThemeDelete.as_view(), name='custom_dashboard/theme_delete'),

                       url(r'^component/(?P<pk>[0-9]+)/$', DashboardComponentList.as_view(), name='dashboard_component_list'),
                       url(r'^component_add/(?P<id>[0-9]+)/$', DashboardComponentCreate.as_view(), name='custom_dashboard/component_add'),
                       url(r'^component_update/(?P<pk>[0-9]+)/$', DashboardComponentUpdate.as_view(template_name="configurabledashboard/components/admin/update_form.html"), name='custom_dashboard/component_update'),
                       url(r'^component_delete/(?P<pk>[0-9]+)/$', DashboardComponentDelete.as_view(), name='custom_dashboard/component_delete'),

                       url(r'^data/(?P<pk>[0-9]+)/$', ComponentDataSourceList.as_view(), name='component_data_source_list'),
                       url(r'^data_add/$', ComponentDataSourceCreate.as_view(), name='custom_dashboard/data_add'),
                       url(r'^data_detail/(?P<pk>[0-9]+)/$', ComponentDataSourceDetail.as_view(), name='custom_data_source_detail'),
                       url(r'^data_assign/(?P<pk>[0-9]+)/$', DashboardComponentUpdate.as_view(template_name="configurabledashboard/datasource/assign.html"), name='custom_dashboard/data_assign'),
                       url(r'^data_update/(?P<pk>[0-9]+)/$', ComponentDataSourceUpdate.as_view(), name='custom_dashboard/data_update'),
                       url(r'^data_delete/(?P<pk>[0-9]+)/$', ComponentDataSourceDelete.as_view(), name='custom_dashboard/data_delete'),
]
