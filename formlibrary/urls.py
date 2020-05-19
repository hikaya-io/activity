#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.views.generic import TemplateView
from django.urls import path
from .views import (
    DistributionCreate,
    DistributionList,
    DistributionListObjects,
    DistributionUpdate,
    GetAgreements,
    IndividualCreate,
    IndividualList,
    IndividualListObjects,
    IndividualUpdate,
    IndividualViewDetail,
    IndividualViewList,
    TrainingCreate,
    TrainingList,
    TrainingListObjects,
    TrainingParticipantListObjects,
    TrainingUpdate,
    add_distribution,
    add_training,
    delete_distribution,
    delete_individual,
    delete_training,
)

# place app url patterns here

urlpatterns = [
    path('comingsoon', TemplateView.as_view(template_name='formlibrary/comingsoon.html')),
    path('training_list/<slug:program>/<slug:project>/', TrainingList.as_view(),
         name='training_list'),
    path('add-training', add_training, name='add_training'),
    path('add-distribution', add_distribution, name='add_distribution'),
    path('training_objects/<slug:program>/<slug:project>/',
         TrainingListObjects.as_view(), name='training_objects'),
    path('training_add/<slug:id>/', TrainingCreate.as_view(),
         name='training_add'),
    path('training_update/<slug:pk>/',
         TrainingUpdate.as_view(), name='training_update'),
    path('training_delete/<slug:pk>/', delete_training,
         name='training_delete'),
    path('training_participants/<int:pk>', TrainingParticipantListObjects.as_view(),
         name='training_participants'),

    path(
        r'individual/<int:pk>/',
        IndividualViewDetail.as_view(),
        name='Individual_detail'
    ),
    path(
        r'individual/',
        IndividualViewList.as_view(),
        name='Individual_list'
    ),
    path('individual_list/<slug:program>/<slug:training>/<slug:distribution>/',
         IndividualList.as_view(), name='individual_list'),
    path('individual_objects/<slug:program>/<slug:project>/',
         IndividualListObjects.as_view(), name='individual_objects'),
    path('individual_add/<slug:id>/',
         IndividualCreate.as_view(), name='individual_add'),
    path('individual_update/<slug:pk>/',
         IndividualUpdate.as_view(), name='individual_update'),
    path('individual_delete/<slug:pk>/',
         delete_individual, name='individual_delete'),

    path('distribution_list/<slug:program>/<slug:project>/',
         DistributionList.as_view(), name='distribution_list'),
    path('distribution_objects/<slug:program>/<slug:project>/',
         DistributionListObjects.as_view(), name='distribution_list'),
    path('distribution_add/<slug:id>/',
         DistributionCreate.as_view(), name='distribution_add'),
    path('distribution_update/<slug:pk>/',
         DistributionUpdate.as_view(), name='distribution_update'),
    path('distribution_delete/<slug:pk>/', delete_distribution,
         name='distribution_delete'),

    path('getagreements/<slug:program>/<slug:project>/',
         GetAgreements.as_view(), name='getagreements'),
]
