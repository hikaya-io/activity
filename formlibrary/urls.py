from django.urls import path, re_path

from .views import (
    IndividualView,
    IndividualList,
    IndividualUpdate,
    GetIndividualData,
    HouseholdView,
    HouseholdlList,
    HouseholdUpdate,
    HouseholdDataView,
    TrainingView,
    TrainingUpdate,
    GetTrainingData,
    DistributionView,
    GetDistributionData,
    ServicelList,
)


urlpatterns = [
    re_path(
        r'individual/(?P<pk>.*)',
        IndividualView.as_view(), name='individual'),

    re_path(
        r'household/(?P<pk>.*)',
        HouseholdView.as_view(),
        name='Households'

    ),

    re_path(
        r'training/(?P<pk>.*)',
        TrainingView.as_view(), name='training'),

    re_path(
        r'distribution/(?P<pk>.*)',
        DistributionView.as_view(), name='distribution'),

    path('individual_list/<slug:program>/<slug:training>/<slug:distribution>/',
         IndividualList.as_view(), name='individual_list'),
    path('individual_update/<slug:pk>/',
         IndividualUpdate.as_view(), name='individual_update'),
    path('individual_data', GetIndividualData.as_view(),
         name='individual_data'),
    path('household_list', HouseholdlList.as_view(), name='household_list'),
    path('household_list_data', HouseholdDataView.as_view(), name='household_list_data'),
    path('household_edit/<int:pk>/', HouseholdUpdate.as_view(), name='household_edit'),

    path('training_update/<slug:pk>/',
         TrainingUpdate.as_view(), name='training_update'),

    path('training_data', GetTrainingData.as_view(),
         name='training_data'),

    path('distribution_update/<slug:pk>/',
         TrainingUpdate.as_view(), name='distribution_update'),

    path('distribution_data', GetDistributionData.as_view(),
         name='distribution_data'),

    path('services_list', ServicelList.as_view(), name='service_list'),

]
