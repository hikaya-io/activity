from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic.edit import UpdateView


from workflow.models import Organization, ActivityUser, Program
from .serializers import HouseholdSerializer, HouseholdListDataSerializer
from .models import Household
from .forms import HouseholdForm


class HouseholdView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = Household.objects.all()
    serializer_class = HouseholdSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        organization = self.request.user.activity_user.organization
        request.data['organization'] = organization.id
        request.data['label'] = organization.household_label
        request.data['program'] = request.data['program'][0] if request.data['program'] else ''
        request.data['created_by'] = self.request.user.activity_user.id
        return self.create(request, *args, **kwargs)

    def get_queryset(self):
        organization = self.request.user.activity_user.organization.id
        return Household.objects.filter(organization=organization)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


def list_households(request):
    user = ActivityUser.objects.filter(user=request.user).first()
    households = Household.objects.filter(organization=user.organization)
    context = {
        'households': households,
        'active': ['formlibrary']
    }
    return render(request, 'formlibrary/household.html', context)


class HouseholdDataView(generics.ListCreateAPIView):

    serializer_class = HouseholdListDataSerializer
    """
    View to fetch all households
    """

    def get_queryset(self):
        organization = self.request.user.activity_user.organization.id
        return Household.objects.filter(organization=organization)

    def get(self, request, *args, **kwargs):
        organization = Organization.objects.get(id=request.user.activity_user.organization.id)
        programs = Program.objects.all().filter(organization=organization).values('id', 'name')

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        data = dict(
                household_label=organization.household_label,
                individual_label=organization.individual_label,
                households=list(serializer.data),
                programs=list(programs),
                safe=False
            )
        return JsonResponse(data)


class HouseholdUpdate(UpdateView):
    model = Household
    template_name = 'formlibrary/household_form.html'
    success_url = '/formlibrary/household_list'
    form_class = HouseholdForm

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(HouseholdUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['organization'] = self.request.user.activity_user.organization
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(HouseholdUpdate, self).get_context_data(**kwargs)
        context['current_household'] = self.get_object()
        context['active'] = ['formlibrary']
        return context
