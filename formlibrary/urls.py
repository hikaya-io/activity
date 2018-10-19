from .views import *

from django.conf.urls import *

# place app url patterns here

urlpatterns = [

                       url(r'^training_list/(?P<pk>\w+)/$', TrainingList.as_view(), name='training_list'),
                       url(r'^training_objects/(?P<program>\w+)/(?P<project>\w+)/$', TrainingListObjects.as_view(), name='training_objects'),
                       url(r'^training_add/(?P<id>\w+)/$', TrainingCreate.as_view(), name='training_add'),
                       url(r'^training_update/(?P<pk>\w+)/$', TrainingUpdate.as_view(), name='training_update'),
                       url(r'^training_delete/(?P<pk>\w+)/$', TrainingDelete.as_view(), name='training_delete'),

                       url(r'^beneficiary_list/(?P<pk>\w+)/$', BeneficiaryList.as_view(), name='beneficiary_list'),
                       url(r'^beneficiary_objects/(?P<program>\w+)/(?P<project>\w+)/$', BeneficiaryListObjects.as_view(), name='beneficiary_objects'),
                       url(r'^beneficiary_add/(?P<id>\w+)/$', BeneficiaryCreate.as_view(), name='beneficiary_add'),
                       url(r'^beneficiary_update/(?P<pk>\w+)/$', BeneficiaryUpdate.as_view(), name='beneficiary_update'),
                       url(r'^beneficiary_delete/(?P<pk>\w+)/$', BeneficiaryDelete.as_view(), name='beneficiary_delete'),

                       url(r'^distribution_list/(?P<pk>\w+)/$', DistributionList.as_view(), name='distribution_list'),
                       url(r'^distribution_objects/(?P<program>\w+)/(?P<project>\w+)/$', DistributionListObjects.as_view(), name='distribution_list'),
                       url(r'^distribution_add/(?P<id>\w+)/$', DistributionCreate.as_view(), name='distribution_add'),
                       url(r'^distribution_update/(?P<pk>\w+)/$', DistributionUpdate.as_view(), name='distribution_update'),
                       url(r'^distribution_delete/(?P<pk>\w+)/$', DistributionDelete.as_view(), name='distribution_delete'),

                        url(r'^getagreements/(?P<program>\w+)/(?P<project>\w+)/$', GetAgreements.as_view(), name='getagreements'),

                       ]
