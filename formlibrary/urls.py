#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .views import (
    TrainingList, add_training, add_distribution, TrainingListObjects,
    IndividualList, IndividualCreate, IndividualListObjects,
    IndividualUpdate, TrainingUpdate, delete_training, delete_beneficiary,
    TrainingCreate, DistributionList, DistributionCreate, DistributionListObjects,
    DistributionUpdate, delete_distribution, GetAgreements,
    TrainingParticipantListObjects)
from django.urls import path

# place app url patterns here

urlpatterns = [
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

    path('beneficiary_list/<slug:program>/<slug:training>/<slug:distribution>/',
         IndividualList.as_view(), name='beneficiary_list'),
    path('beneficiary_objects/<slug:program>/<slug:project>/',
         IndividualListObjects.as_view(), name='beneficiary_objects'),
    path('beneficiary_add/<slug:id>/',
         IndividualCreate.as_view(), name='beneficiary_add'),
    path('beneficiary_update/<slug:pk>/',
         IndividualUpdate.as_view(), name='beneficiary_update'),
    path('beneficiary_delete/<slug:pk>/',
         delete_beneficiary, name='beneficiary_delete'),

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
