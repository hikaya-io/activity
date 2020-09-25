from django.urls import path, re_path

from .views import (
    IndividualView,
    IndividualList,
    IndividualUpdate,
    GetIndividualData,
)


urlpatterns = [
    re_path(
         r'individual/(?P<pk>.*)',
         IndividualView.as_view(), name='individual'),


    path('individual_list/<slug:program>/<slug:training>/<slug:distribution>/',
         IndividualList.as_view(), name='individual_list'),
    path('individual_update/<slug:pk>/',
         IndividualUpdate.as_view(), name='individual_update'),
    path('individual_data', GetIndividualData.as_view(),
         name='individual_data'),

]
