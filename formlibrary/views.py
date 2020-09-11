from django.shortcuts import render
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from django.shortcuts import redirect

from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from workflow.models import Program

from .forms import IndividualForm
from .models import Individual, Distribution, Training

from .serializers import IndividualSerializer


class IndividualCreate(ListCreateAPIView, RetrieveUpdateDestroyAPIView):
    queryset = Individual.objects.all()
    serializer_class = IndividualSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get_queryset(self):
        organization = self.request.user.activity_user.organization.id
        return Individual.objects.filter(organization=organization)


class IndividualList(ListView):
    """
    Individual
    """
    model = Individual
    template_name = 'formlibrary/individual_list.html'
    
    def get(self, request, *args, **kwargs):

        program_id = self.kwargs['program']
        training_id = self.kwargs['training']
        distribution_id = self.kwargs['distribution']

        organization = request.user.activity_user.organization
        get_programs = Program.objects.all().filter(organization=organization)

        get_training = Training.objects.filter(
            program__in=get_programs)
        get_distribution = Distribution.objects.filter(
            program__in=get_programs)
        get_individuals = Individual.objects.filter(
            program__in=get_programs)

        if int(program_id) != 0:
            get_individuals = Individual.objects.filter(
                program__id__contains=program_id)
        if int(training_id) != 0:
            get_individuals = Individual.objects.filter(
                training__id=int(training_id))
        if int(distribution_id) != 0:
            get_individuals = Individual.objects.filter(
                distribution__id=int(distribution_id))

        return render(request, self.template_name,
                      {
                          'get_individuals': get_individuals,
                          'program_id': int(program_id),
                          'get_programs': get_programs,
                          'get_distribution': get_distribution,
                          'get_training': get_training,
                          'training_id': int(training_id),
                          'distribution_id': int(distribution_id),
                          'form_component': 'individual_list',
                          'active': ['forms', 'individual_list']
                      })

class IndividualUpdate(UpdateView):
    """
    Training Form
    """
    model = Individual
    template_name = 'formlibrary/individual_form.html'
    success_url = '/formlibrary/individual_list/0/0/0'
    form_class = IndividualForm

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(IndividualUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['organization'] = self.request.user.activity_user.organization
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(IndividualUpdate, self).get_context_data(**kwargs)
        context['current_program'] = self.get_object()
        context['active'] = ['formlibrary']
        return context

def delete_individual(request, pk):
    individual = Individual.objects.get(pk=int(pk))
    individual.delete()

    return redirect('/formlibrary/individual_list/0/0/0/')

