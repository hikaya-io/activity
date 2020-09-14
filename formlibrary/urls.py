from django.urls import path, re_path


from .views import (
    HouseholdView, list_households, HouseholdUpdate, HouseholdDataView
)


urlpatterns = [
    re_path(
        r'household/(?P<pk>.*)',
        HouseholdView.as_view(),
        name='Households'

    ),

    path('household_list', list_households, name='household_list'),
    path('household_list_data', HouseholdDataView.as_view(), name='household_list_data'),
    path('household_edit/<int:pk>/', HouseholdUpdate.as_view(), name='household_edit')
]
