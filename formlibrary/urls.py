from django.urls import path

from .views import (
    IndividualCreate,
    IndividualList,
    IndividualUpdate,
    delete_individual,
)


urlpatterns = [
    path('individual_list/<slug:program>/<slug:training>/<slug:distribution>/',
         IndividualList.as_view(), name='individual_list'),
    path('individual_add/<slug:id>/',
            IndividualCreate.as_view(), name='individual_add'),
    path('individual_update/<slug:pk>/',
         IndividualUpdate.as_view(), name='individual_update'),
    path('individual_delete/<slug:pk>/',
         delete_individual, name='individual_delete'),

]
