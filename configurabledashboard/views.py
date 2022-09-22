#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .mixins import AjaxableResponseMixin
from activity.util import group_excluded
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import CustomDashboard, DashboardComponent, ComponentDataSource, \
    DashboardTheme
from workflow.models import Program, FormGuidance
from .forms import (
    CustomDashboardCreateForm, CustomDashboardForm, CustomDashboardModalForm,
    DashboardThemeCreateForm, DashboardThemeForm,
    DashboardComponentCreateForm, DashboardComponentForm,
    ComponentDataSourceForm,
    ComponentDataSourceCreateForm
)

from django.shortcuts import render
from django.contrib import messages
import json
from collections import OrderedDict
import requests
import logging
from django.http import HttpResponse, HttpResponseRedirect

# Get an instance of a logger
logger = logging.getLogger(__name__)


# CLASS VIEWS FOR THE DASHBOARD OBJECT
# ===========================================
# This lists available custom dashboards to view
class CustomDashboardList(ListView):
    model = CustomDashboard
    template_name = 'configurabledashboard/dashboard/list.html'

    def get(self, request, *args, **kwargs):
        # retrieve program
        model = Program  # noqa
        program_id = int(self.kwargs['pk'])
        get_program = Program.objects.all().filter(id=program_id)

        # retrieve the coutries the user has data access for
        # countries = get_country(request.user)

        # retrieve projects for a program
        # get_projects = ProjectAgreement.objects.all()
        #   .filter(program__id=program__id, program__country__in=countries)

        # retrieve projects for a program
        get_custom_dashboards = CustomDashboard.objects.all() \
            .filter(program=program_id)

        return render(request, self.template_name, {
            'pk': program_id, 'get_custom_dashboards': get_custom_dashboards,
            'get_program': get_program})


class CustomDashboardCreate(CreateView):
    #   :param request:
    #   :param id:
    #   """
    model = CustomDashboard
    template_name = 'configurabledashboard/dashboard/form.html'
    guidance = None

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="CustomDashboard")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(CustomDashboardCreate, self).dispatch(request, *args,
                                                           **kwargs)

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(CustomDashboardCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_initial(self):
        initial = {}
        return initial

    def get_context_data(self, **kwargs):
        context = super(CustomDashboardCreate, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        context.update({'pk': pk})
        return context

    def form_invalid(self, form):

        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        if form.is_valid():
            data = form.save(commit=False)
            form_theme = data.theme
            get_selected_theme = DashboardTheme.objects.all().filter(
                id=form_theme.id)
            parsed_layout = json.loads(
                get_selected_theme[0].layout_dictionary,
                object_pairs_hook=OrderedDict)
            new_map = {}
            for key in parsed_layout:
                new_map[key] = "NONE"
            data.component_map = json.dumps(new_map)
            data.save()

        # save formset from context
        # context = self.get_context_data()

        messages.success(self.request, 'Success, Dashboard Created!')
        redirect_url = '/configurabledashboard/' + str(self.kwargs['pk'])
        return HttpResponseRedirect(redirect_url)

    form_class = CustomDashboardCreateForm


class CustomDashboardDetail(DetailView):
    model = CustomDashboard

    def get_template_names(self):
        dashboard = CustomDashboard.objects.get(id=self.kwargs['pk'])
        get_dashboard_theme = DashboardTheme.objects.all().filter(
            id=dashboard.theme.id)
        template_name = get_dashboard_theme[0].theme_template
        return template_name

    def get_context_data(self, **kwargs):
        context = super(CustomDashboardDetail, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        context.update({'pk': pk})

        try:
            get_custom_dashboard = CustomDashboard.objects.get(
                id=self.kwargs['pk'])
        except CustomDashboard.DoesNotExist:
            get_custom_dashboard = None
        context.update({'get_custom_dashboard': get_custom_dashboard})

        try:
            selected_theme = get_custom_dashboard.theme.id
            get_dashboard_theme = DashboardTheme.objects.all().filter(
                id=selected_theme)
        except DashboardTheme.DoesNotExist:
            get_dashboard_theme = None
        context.update({'get_dashboard_theme': get_dashboard_theme})

        try:
            get_dashboard_components = get_custom_dashboard.components.all()
        except DashboardComponent.DoesNotExist:
            get_dashboard_components = None
        context.update({'get_dashboard_components': get_dashboard_components})

        try:
            color_selection = get_custom_dashboard.color_palette
            if color_selection == 'bright':
                get_color_palette = [
                    '#82BC00', '#C8C500', '#10A400', '#CF102E',
                    '#DB5E11', '#A40D7A', '#00AFA8',
                    '#1349BB', '#FFD200', '#FF7100', '#FFFD00',
                    '#ABABAB', '#7F7F7F', '#7B5213', '#C18A34'],
            else:
                get_color_palette = [
                    '#BAEE46', '#FDFB4A', '#4BCF3D', '#F2637A',
                    '#FFA268', '#C451A4', '#4BC3BE', '#FFD592'
                    '#5B7FCC', '#9F54CC', '#FFE464', '#FFA964',
                    '#FFFE64', '#D7D7D7', '#7F7F7F', '#D2A868',
                   ]
        except get_custom_dashboard.DoesNotExist:
            get_color_palette = None
        context.update({'get_color_palette': get_color_palette})

        try:
            get_component_order = json.loads(
                get_custom_dashboard.component_map)
        except not get_custom_dashboard.component_map:
            get_component_order = None
        context.update({'get_component_order': get_component_order})
        # retrieve the data source mapping of data
        try:
            get_component_data_maps = {}
            for position, component_id in get_component_order.items():
                # add an attribute to the get_component_data_maps dictionary
                # for all data from this component
                selected_id = int(component_id)
                selected_component = DashboardComponent.objects.get(
                    id=selected_id)
                get_component_data_maps[position] = {}
                get_component_data_maps[position]['component_id'] = selected_id
                get_component_data_maps[position][
                    'data_map'] = selected_component.data_map
        except not get_custom_dashboard.component_map:
            get_component_data_maps = None
        context.update({'get_component_data_maps': get_component_data_maps})

        # retrieve data for each componennt in data map
        # try:
        #     get_all_component_data = {}
        # #     #iterate through the component maps for each position on the page
        # # for position in get_component_data_maps:
        # #         #iterate through the data sources mapped for each
        # #         components and retrieve data
        # #         for mapped_item, data_source in
        # #           get_component_data_maps[position]['data_map']:
        # #             # get that DataSource by id
        # #             data_source =
        # #               ComponentDataSource.objects.get(data_source)
        # #             #retrieve data
        # #             dataset = data_source.data_source  # do JSON request here
        # #             # filter data by the key to just use subset needed
        # #             filtered_data = dataset[data_source.filter_key]
        # #             get_all_component_data[position]['data_sources']
        # #               ['data_source.name'] = filtered_data
        # except not getDashboardComponentDataMaps:
        #     get_all_component_data = None
        # context.update({'get_all_component_data': get_all_component_data})

        return context


# TODO: build out function for component mapping for dashboard wizard


# component_map):
# def custom_dashboard_update_components(AjaxableResponseMixin, pk, location,
#                                        type):
#     # (?P<pk>[0-9]+)/(?P<location>[0-9]+)/(?P<type>[-\w]+)/$
#     # form_mapping = component_map
#     mapped = False
#     current_dashboard = CustomDashboard.objects.get(id=self.kwargs['pk'])
#     current_map = current_dashboard.component_map  # .split("]","],")
#     # for mapped_object in current_map:
#     #     if mapping.0 == form_mapping.0
#     #         update = current_dashboard.update(component_map=form_mapping)
#     #         mapped = true
#     # if mapped == false:
#     #     update = current_dashboard.component_map.append(form_mapping)
#     #     current_dashboard.save()
#     return HttpResponse(component_map)


class CustomDashboardUpdate(UpdateView):
    model = CustomDashboard
    form_class = CustomDashboardForm
    guidance = None

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="CustomDashboard")
        except FormGuidance.DoesNotExist:
            self.guidance = None

        return super(CustomDashboardUpdate, self).dispatch(request, *args,
                                                           **kwargs)

    def get_initial(self):
        get_custom_dashboard = CustomDashboard.objects.get(id=self.kwargs['pk'])
        get_dashboard_components = DashboardComponent.objects.all().filter(
            componentset=get_custom_dashboard)
        get_all_component_data_sources = ComponentDataSource.objects.all()
        initial = {
            'get_custom_dashboard': get_custom_dashboard,
            'get_dashboard_components': get_dashboard_components,
            'get_all_component_data_sources': get_all_component_data_sources,
        }

        return initial

    def get_form(self, form_class):
        check_form_type = self.request.get_full_path()
        if check_form_type.startswith('/configurabledashboard/edit'):
            form = CustomDashboardModalForm
        else:
            form = CustomDashboardForm

        return form(**self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        context = super(CustomDashboardUpdate, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        context.update({'pk': pk})

        check_path = self.request.get_full_path()
        if check_path.startswith('/confirgureabledashboard/map'):
            location = self.kwargs['location']
            component_type = self.kwargs['type']
        # TODO: If applicable, work through flow for remapping
        # else if check_form_type.startswith('/confirgureabledashboard/remap'):
        #     location = self.kwargs['location']
        #     component_type = self.kwargs['type']
        else:
            location = None
            component_type = None
        context.update({'location': location})
        context.update({'component_type': component_type})

        try:
            get_custom_dashboard = CustomDashboard.objects.get(
                id=self.kwargs['pk'])
        except CustomDashboard.DoesNotExist:
            get_custom_dashboard = None
        context.update({'get_custom_dashboard': get_custom_dashboard})

        try:
            selected_theme = get_custom_dashboard.theme
            get_dashboard_theme = DashboardTheme.objects.all().filter(
                id=selected_theme.id)
        except DashboardTheme.DoesNotExist:
            get_dashboard_theme = None
        context.update({'get_dashboard_theme': get_dashboard_theme})

        # This theme layout helps to map the components to their position
        # on the page
        # Dashboard layout should be pairs of the # position in
        # the template (1,2,3...) and the component type that needs to be
        # slotted into that position

        if get_dashboard_theme:
            layout = get_dashboard_theme[0].layout_dictionary
            get_dashboard_layout_list = json.loads(
                layout, object_pairs_hook=OrderedDict)
        else:
            get_dashboard_layout_list = None
        context.update({'get_dashboard_layout_list': get_dashboard_layout_list})

        try:
            get_dashboard_components = DashboardComponent.objects.all().filter(
                componentset=get_custom_dashboard)
        except DashboardComponent.DoesNotExist:
            get_dashboard_components = None
        context.update({'get_dashboard_components': get_dashboard_components})

        try:
            get_component_order = json.loads(
                get_custom_dashboard.component_map,
                object_pairs_hook=OrderedDict)
        except Exception:
            get_component_order = None
        context.update({'get_component_order': get_component_order})

        try:
            get_all_component_maps = []
            for component in get_dashboard_components:
                if component.data_map:
                    get_all_component_maps[component] = json.loads(
                        component.data_map)
        except not get_dashboard_components:
            get_all_component_maps = None
        context.update({'get_all_component_maps': get_all_component_maps})

        try:
            get_all_component_data_sources = ComponentDataSource.objects.all()
        except ComponentDataSource.DoesNotExist:
            get_all_component_data_sources = None
        context.update(
            {'get_all_component_data_sources': get_all_component_data_sources})

        # try:
        #     getAllDataFilters = {}
        #     for data_source in get_all_component_data_sources:
        #         data_source_filters = import_data_filter_options(
        #           data_source.data_source, data_source.data_filter_key,
        #           data_source.authorization_token)
        #         getAllDataFilters[data_source.id] = data_source_filters
        # except not get_all_component_data_sources:
        #     getAllDataFilters = None
        # context.update({'getAllDataFilters': getAllDataFilters})

        mapped_location = self.request.GET.get('location')
        component_type = self.request.GET.get('type')
        if mapped_location and component_type:
            context.update({'mapped_location': mapped_location})
            context.update({'component_type': component_type})

        return context

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(CustomDashboardUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_invalid(self, form):
        messages.error(self.request, self, fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        # check_form_type = self.request.get_full_path()
        # TODO: Once refactoring is done, revisit
        #  whether checking form type still needed
        # if check_form_type.startswith('/confirgureabledashboard/map'):
        #     get_custom_dashboard.component_map =
        #       form.cleaned_data['component_map']
        #     get_custom_dashboard.save()
        # for position in get_custom_dashboard.component_map:
        #     mapped_position = form.component_map.0
        #     if position.0 == mapped_position:
        #         position.1 == form.component_map.1
        #         mapped = true
        # if mapped != true:
        #     get_custom_dashboard.component_map.append(form.component_map)
        # else:
        form.save()
        messages.success(
            self.request, 'Success, CustomDashboard Output Updated!')

        return self.render_to_response(self.get_context_data(form=form))


# TODO: build out code to import data filters
#  for modal to select filters on wizard

def import_data_filter_options(data_url, column_filter, authorization_token):
    """
    For populating data filters in dropdown --
        retrieve data_source using data_url
    """
    # filter_url = data_url
    headers = {'content-type': 'application/json',
               'Authorization': authorization_token}
    response = requests.get(data_url, headers=headers, verify=False)
    get_json = json.loads(response.content)
    data = get_json
    data_filters = data[column_filter]
    return HttpResponse(data_filters, content_type="application/json")


class CustomDashboardDelete(AjaxableResponseMixin, DeleteView):
    """
    CustomDashboard Delete
    """
    model = CustomDashboard
    template_name = 'configurabledashboard/dashboard/confirm_delete.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(CustomDashboardDelete, self).get_context_data(**kwargs)
        # get_custom_dashboard = CustomDashboard.objects.all().get(
        #     id=self.kwargs['pk'])
        # pk = self.kwargs['pk']
        context.update({'pk': self.kwargs['pk']})
        return context

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Dashboard Deleted!')
        return self.render_to_response(self.get_context_data(form=form))

    form_class = CustomDashboardForm


# CLASS VIEWS FOR THE THEME OBJECT
# Note: theme_layout must be in a string/JSON format like this:
# {"1": "context_pane","2": "content_map",
#  "3": "bar_graph","4": "sidebar_events"}
# ===========================================


class DashboardThemeList(ListView):
    model = CustomDashboard
    template_name = 'configurabledashboard/themes/admin/list.html'

    def get(self, request, *args, **kwargs):
        get_dashboard_themes = DashboardTheme.objects.all()
        return render(request, self.template_name,
                      {'get_dashboard_themes': get_dashboard_themes})


class DashboardThemeCreate(CreateView):
    model = DashboardTheme
    template_name = 'configurabledashboard/themes/admin/form.html'
    guidance = None

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(DashboardThemeCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="DashboardTheme")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(DashboardThemeCreate, self).dispatch(request, *args,
                                                          **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DashboardThemeCreate, self).get_context_data(**kwargs)

        return context

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Theme Created!')
        return self.render_to_response(self.get_context_data(form=form))

    form_class = DashboardThemeCreateForm


class DashboardThemeUpdate(UpdateView):
    model = DashboardTheme
    template_name = 'configurabledashboard/themes/admin/update_form.html'

    def dispatch(self, request, *args, **kwargs):
        return super(DashboardThemeUpdate, self).dispatch(request, *args,
                                                          **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DashboardThemeUpdate, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        context.update({'pk': pk})
        get_complete = DashboardTheme.objects.get(id=self.kwargs['pk'])
        context.update({'get_complete': get_complete})
        return context

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(DashboardThemeUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        self.object = form.save()

        messages.success(self.request, 'Success, form updated!')

        return self.render_to_response(self.get_context_data(form=form))

    form_class = DashboardThemeForm


class DashboardThemeDelete(DeleteView):
    """
    DashboardTheme Delete
    """
    model = DashboardTheme
    template_name = 'configurabledashboard/themes/admin/confirm_delete.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(DashboardThemeDelete, self).get_context_data(**kwargs)
        context.update({'pk': self.kwargs['pk']})
        return context

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()

        messages.success(self.request, 'Success, Dashboard Theme Deleted!')
        return self.render_to_response(self.get_context_data(form=form))

    form_class = DashboardThemeForm


# CLASS VIEWS FOR THE DASHBOARD COMPONENT OBJECT
# ===========================================


class DashboardComponentList(ListView):
    model = DashboardComponent
    template_name = 'configurabledashboard/components/admin/list.html'

    def get(self, request, *args, **kwargs):
        # retrieve program
        model = Program  # noqa
        # retrieve the countries the user has data access for
        # countries = get_country(request.user)
        dashboard_id = int(self.kwargs['pk'])

        get_dashboard_list_components = DashboardComponent.objects.all()\
            .filter(componentset=dashboard_id)

        return render(request, self.template_name, {
            'get_dashboard_list_components': get_dashboard_list_components})


class DashboardComponentCreate(CreateView):
    model = DashboardComponent
    template_name = 'configurabledashboard/components/admin/form.html'
    guidance = None

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(DashboardComponentCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        # id = self.kwargs['id']
        return kwargs

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="DashboardComponent")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(DashboardComponentCreate, self).dispatch(request, *args,
                                                              **kwargs)

    def get_initial(self):
        initial = {
            'get_custom_dashboard': CustomDashboard.objects.get(
                id=self.kwargs['id']),
            'get_component_data_sources': ComponentDataSource.objects.all(),
        }
        return initial

    def get_context_data(self, **kwargs):
        context = super(DashboardComponentCreate,
                        self).get_context_data(**kwargs)
        try:
            get_custom_dashboard = CustomDashboard.objects.get(
                id=self.kwargs['id'])
        except CustomDashboard.DoesNotExist:
            get_custom_dashboard = None
        context.update({'get_custom_dashboard': get_custom_dashboard})

        return context

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        # context = self.get_context_data()
        messages.success(self.request, 'Success, Component Created!')
        latest_component = DashboardComponent.objects.latest('id')
        get_custom_dashboard = CustomDashboard.objects.get(id=self.kwargs['id'])
        get_custom_dashboard.components.add(latest_component)
        return self.render_to_response(self.get_context_data(form=form))

    form_class = DashboardComponentCreateForm


class DashboardComponentUpdate(UpdateView):
    model = DashboardComponent
    success_url = '/'

    def dispatch(self, request, *args, **kwargs):
        # try:
        #     guidance = FormGuidance.objects.get(
        #           form="DashboardComponentUpdate")
        # except FormGuidance.DoesNotExist:
        #     guidance = None
        return super(DashboardComponentUpdate, self).dispatch(request, *args,
                                                              **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DashboardComponentUpdate,
                        self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        context.update({'pk': pk})

        # get_component_data_sources = []
        get_component_data_sources = ComponentDataSource.objects.all()
        context.update(
            {'get_component_data_sources': get_component_data_sources})

        get_dashboard_component = DashboardComponent.objects.all().get(
            id=self.kwargs['pk'])
        context.update({'get_dashboard_component': get_dashboard_component})

        # for each component define the properties the component
        # needs to have data mapped for by type
        # ideally this dictionary would be saved externally as a constant
        get_component_properties = {
            'bar_graph': {'labels': '', 'data': '', 'colors': ''},
            'doughnut': {'labels': '', 'data': '', 'colors': ''},
            'line': {'labels': '', 'data': '', 'colors': ''},
            'pie': {'labels': '', 'data': '', 'colors': ''},
            'polar': {'labels': '', 'data': '', 'colors': ''},
            'radar': {'labels': '', 'data': '', 'colors': ''},
            'sidebar_gallery': {'photo_url': '', 'photo_titles': '',
                                'photo_captions': '', 'photo_dates': ''},
            'content_map': {'latitude': '', 'longitude': '',
                            'location_name': '', 'description': '',
                            'region_link': '', 'region_name': ''},
            'region_map': {'latitude': '', 'longitude': '', 'site_contact': '',
                           'location_name': '', 'description': ''},
            'sidebar_map': {'latitude': '', 'longitude': '',
                            'site_contact': '', 'location_name': '',
                            'description': ''},
            'context_pane': {},
            'sidebar_events': {},
            'sidebar_news': {},
            'sidebar_objectives': {}
        }
        context.update({'get_component_properties': get_component_properties})
        return context

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(DashboardComponentUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        self.object = form.save()

        messages.success(self.request, 'Success, form updated!')

        return self.render_to_response(self.get_context_data(form=form))

    form_class = DashboardComponentForm


class DashboardComponentDelete(AjaxableResponseMixin, DeleteView):
    model = DashboardComponent
    template_name = 'configurabledashboard/components/confirm_delete.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(DashboardComponentDelete,
                        self).get_context_data(**kwargs)
        context.update({'pk': self.kwargs['pk']})
        return context

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Component Deleted!')
        return self.render_to_response(self.get_context_data(form=form))

    form_class = DashboardComponentForm


class ComponentDataSourceList(ListView):
    model = ComponentDataSource
    template_name = 'configurabledashboard/datasource/list.html'

    def get(self, request, *args, **kwargs):
        get_component_data_sources = ComponentDataSource.objects.all()

        return render(request, self.template_name,
                      {'get_component_data_sources': get_component_data_sources})


# CLASS VIEWS FOR THE DATA SOURCE OBJECT
# ===========================================
class ComponentDataSourceCreate(CreateView):
    model = ComponentDataSource
    template_name = 'configurabledashboard/datasource/form.html'

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(ComponentDataSourceCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        return super(ComponentDataSourceCreate, self).dispatch(request, *args,
                                                               **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ComponentDataSourceCreate,
                        self).get_context_data(**kwargs)
        return context

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        # context = self.get_context_data()
        messages.success(self.request, 'Success, Data Source Created!')
        return self.render_to_response(self.get_context_data(form=form))

    form_class = ComponentDataSourceCreateForm


class ComponentDataSourceDetail(DetailView):
    model = ComponentDataSource
    template_name = 'configurabledashboard/datasource/detail.html'

    def get(self, request, *args, **kwargs):
        get_component_data_sources = ComponentDataSource.objects.all()

        return render(request, self.template_name,
                      {'get_component_data_sources': get_component_data_sources})


class ComponentDataSourceUpdate(UpdateView):
    model = ComponentDataSource
    template_name = 'configurabledashboard/datasource/update_form.html'
    guidance = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="ComponentDataSource")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(ComponentDataSourceUpdate, self).dispatch(request, *args,
                                                               **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ComponentDataSourceUpdate,
                        self).get_context_data(**kwargs)
        # get_component_data_source = ComponentDataSource.objects.all().get(
        #     id=self.kwargs['pk'])
        pk = self.kwargs['pk']
        context.update({'pk': pk})

        # get stuff
        return context

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(ComponentDataSourceUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    # get shared data from project agreement and pre-populate form with it
    def get_initial(self):
        initial = {}
        return initial

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        self.object = form.save()

        messages.success(self.request, 'Success, form updated!')

        return self.render_to_response(self.get_context_data(form=form))

    form_class = ComponentDataSourceForm


class ComponentDataSourceDelete(AjaxableResponseMixin, DeleteView):
    model = ComponentDataSource
    template_name = 'configurabledashboard/datasource/confirm_delete.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(ComponentDataSourceDelete,
                        self).get_context_data(**kwargs)
        # get_data_source = ComponentDataSource.objects.all().get(
        #     id=self.kwargs['pk'])
        # pk = self.kwargs['pk']
        context.update({'pk': self.kwargs['pk']})
        return context

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Success, Component Deleted!')
        return self.render_to_response(self.get_context_data(form=form))

    form_class = ComponentDataSourceForm
