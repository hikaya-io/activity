from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import CustomDashboard, DashboardComponent, ComponentDataSource, DashboardTheme
from workflow.models import Program, FormGuidance
from .forms import CustomDashboardCreateForm, CustomDashboardForm, CustomDashboardModalForm, \
    CustomDashboardMapForm, DashboardThemeCreateForm, DashboardThemeForm, DashboardComponentCreateForm, DashboardComponentForm, ComponentDataSourceForm, \
    ComponentDataSourceCreateForm

from django.shortcuts import render
from django.contrib import messages
import json
from collections import OrderedDict
import requests
import logging
from django.http import HttpResponse, HttpResponseRedirect

# Get an instance of a logger
logger = logging.getLogger(__name__)

from django.utils.decorators import method_decorator
from tola.util import getCountry, group_excluded
from mixins import AjaxableResponseMixin


# CLASS VIEWS FOR THE DASHBOARD OBJECT
# ===========================================
# This lists available custom dashboards to view
class CustomDashboardList(ListView):
    """
    CustomDashboard
    :param request:
    :param pk: program_id
    """
    model = CustomDashboard
    template_name = 'configurabledashboard/dashboard/list.html'

    def get(self, request, *args, **kwargs):
    ## retrieve program
        model = Program
        program_id = int(self.kwargs['pk'])
        getProgram = Program.objects.all().filter(id=program_id)

        ## retrieve the coutries the user has data access for
        countries = getCountry(request.user)

        #retrieve projects for a program
        # getProjects = ProjectAgreement.objects.all().filter(program__id=program__id, program__country__in=countries)

        #retrieve projects for a program
        getCustomDashboards = CustomDashboard.objects.all().filter(program=program_id)
            
        return render(request, self.template_name, {'pk': program_id, 'getCustomDashboards': getCustomDashboards, 'getProgram': getProgram})


class CustomDashboardCreate(CreateView):
    #   :param request:
    #   :param id:
    #   """
    model = CustomDashboard
    template_name = 'configurabledashboard/dashboard/form.html'

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            self.guidance = FormGuidance.objects.get(form="CustomDashboard")
        except FormGuidance.DoesNotExist:
            self.guidance = None
        return super(CustomDashboardCreate, self).dispatch(request, *args, **kwargs)

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
            getSelectedTheme = DashboardTheme.objects.all().filter(id=form_theme.id)
            parsedLayout = json.loads(getSelectedTheme[0].layout_dictionary, object_pairs_hook=OrderedDict)
            new_map = {}
            for key in parsedLayout:
                new_map[key] = "NONE"
            data.component_map = json.dumps(new_map)
            data.save()

        #save formset from context
        context = self.get_context_data()

        messages.success(self.request, 'Success, Dashboard Created!')
        redirect_url = '/configurabledashboard/' + str(self.kwargs['pk'])
        return HttpResponseRedirect(redirect_url)

    form_class = CustomDashboardCreateForm 


class CustomDashboardDetail(DetailView):

    model = CustomDashboard

    def get_template_names(self):
        dashboard = CustomDashboard.objects.get(id = self.kwargs['pk'])
        getDashboardTheme = DashboardTheme.objects.all().filter(id = dashboard.theme.id)
        template_name = getDashboardTheme[0].theme_template
        return template_name

    def get_context_data(self, **kwargs):
        context = super(CustomDashboardDetail, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        context.update({'pk': pk})

        try:
            getCustomDashboard =CustomDashboard.objects.get(id=self.kwargs['pk'])
        except CustomDashboard.DoesNotExist:
            getCustomDashboard = None
        context.update({'getCustomDashboard': getCustomDashboard})

        try:
            selected_theme = getCustomDashboard.theme.id
            getDashboardTheme = DashboardTheme.objects.all().filter(id=selected_theme)
        except DashboardTheme.DoesNotExist:
            getDashboardTheme = None
        context.update({'getDashboardTheme': getDashboardTheme})

        try:
            getDashboardComponents = getCustomDashboard.components.all()
        except DashboardComponent.DoesNotExist:
            getDashboardComponents = None
        context.update({'getDashboardComponents': getDashboardComponents})
        
        try:
            color_selection = getCustomDashboard.color_palette
            if color_selection == 'bright':
                getColorPalette = ['#82BC00','#C8C500','#10A400','#CF102E','#DB5E11','#A40D7A','#00AFA8','#1349BB','#FFD200','#FF7100','#FFFD00','#ABABAB','#7F7F7F','#7B5213','#C18A34'],
            else:
                getColorPalette = ['#BAEE46','#FDFB4A','#4BCF3D','#F2637A','#FFA268','#C451A4','#4BC3BE','#5B7FCC','#9F54CC','#FFE464','#FFA964','#FFFE64','#D7D7D7','#7F7F7F','#D2A868','#FFD592']
        except getCustomDashboard.DoesNotExist:
                getColorPalette = None
        context.update({'getColorPalette': getColorPalette})

        try:
            getComponentOrder = json.loads(getCustomDashboard.component_map)
        except not getCustomDashboard.component_map:
            getComponentOrder = None
        context.update({'getComponentOrder': getComponentOrder})
        # retrieve the data source mapping of data 
        try:
            getComponentDataMaps = {}
            for position, component_id in getComponentOrder.items():
                #add an attribute to the getComponentDataMaps dictionary for all data from this component
                selected_id = int(component_id)
                selected_component = DashboardComponent.objects.get(id = selected_id)
                getComponentDataMaps[position] = {}
                getComponentDataMaps[position]['component_id'] = selected_id
                getComponentDataMaps[position]['data_map'] = selected_component.data_map
        except not getCustomDashboard.component_map:
            getComponentDataMaps = None
        context.update({'getComponentDataMaps': getComponentDataMaps})

        #retrieve data for each componennt in data map
        try:
            getAllComponentData = {}
        #     #iterate through the component maps for each position on the page
            # for position in getComponentDataMaps:
        #         #iterate through the data sources mapped for each components and retrieve data
        #         for mapped_item, data_source in getComponentDataMaps[position]['data_map']:
        #             # get that DataSource by id
        #             data_source = ComponentDataSource.objects.get(data_source)
        #             #retrieve data 
        #             dataset = data_source.data_source  # do JSON request here
        #             # filter data by the key to just use subset needed
        #             filtered_data = dataset[data_source.filter_key]
        #             getAllComponentData[position]['data_sources']['data_source.name'] = filtered_data
        except not getDashboardComponentDataMaps:
            getAllComponentData = None
        context.update({'getAllComponentData': getAllComponentData})
        
        return context

#TODO: build out function for component mapping for dashboard wizard
def custom_dashboard_update_components(AjaxableResponseMixin,pk,location,type): #component_map):
# (?P<pk>[0-9]+)/(?P<location>[0-9]+)/(?P<type>[-\w]+)/$
    # form_mapping = component_map
    mapped = false
    current_dashboard = CustomDashboard.objects.get(id=self.kwargs['pk'])
    current_map = current_dashboard.component_map#.split("]","],")
    # for mapped_object in current_map:
    #     if mapping.0 == form_mapping.0
    #         update = current_dashboard.update(component_map=form_mapping)
    #         mapped = true
    # if mapped == false:
    #     update = current_dashboard.component_map.append(form_mapping)
    #     current_dashboard.save()
    return HttpResponse(component_map)


class CustomDashboardUpdate(UpdateView):

    model = CustomDashboard
    form_class = CustomDashboardForm

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            guidance = FormGuidance.objects.get(form="CustomDashboard")
        except FormGuidance.DoesNotExist:
            guidance = None
        
        return super(CustomDashboardUpdate, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        getCustomDashboard = CustomDashboard.objects.get(id=self.kwargs['pk'])
        getDashboardComponents = DashboardComponent.objects.all().filter(componentset=getCustomDashboard)
        getAllComponentDataSources = ComponentDataSource.objects.all()
        initial = {
            'getCustomDashboard': getCustomDashboard,
            'getDashboardComponents': getDashboardComponents,
            'getAllComponentDataSources': getAllComponentDataSources,
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
            getCustomDashboard =CustomDashboard.objects.get(id=self.kwargs['pk'])
        except CustomDashboard.DoesNotExist:
            getCustomDashboard = None
        context.update({'getCustomDashboard': getCustomDashboard})

        try:
            selected_theme = getCustomDashboard.theme
            getDashboardTheme = DashboardTheme.objects.all().filter(id=selected_theme.id)
        except DashboardTheme.DoesNotExist:
            getDashboardTheme = None   
        context.update({'getDashboardTheme': getDashboardTheme})

        # This theme layout helps to map the components to their position on the page
        # Dashboard layout should be pairs of the # position in the template (1,2,3...) and 
        # the component type that needs to be slotted into that position
        
        if getDashboardTheme:
            getDashboardTheme[0].layout_dictionary
            layout = getDashboardTheme[0].layout_dictionary
            getDashboardLayoutList = json.loads(layout, object_pairs_hook=OrderedDict)
        else: 
            getDashboardLayoutList = None
        context.update({'getDashboardLayoutList': getDashboardLayoutList})

        try:
            getDashboardComponents = DashboardComponent.objects.all().filter(componentset=getCustomDashboard)
        except DashboardComponent.DoesNotExist:
            getDashboardComponents = None
        context.update({'getDashboardComponents': getDashboardComponents})

        try: 
            getComponentOrder = json.loads(getCustomDashboard.component_map, object_pairs_hook=OrderedDict)
        except:
            getComponentOrder = None
        context.update({'getComponentOrder': getComponentOrder})

        try: 
            getAllComponentMaps = []
            for component in getDashboardComponents:
                if component.data_map:
                    getAllComponentMaps[component] = json.loads(component.data_map)
        except not getDashboardComponents:
            getAllComponentMaps = None
        context.update({'getAllComponentMaps': getAllComponentMaps})

        try:
            getAllComponentDataSources = ComponentDataSource.objects.all()
        except ComponentDataSource.DoesNotExist:
            getAllComponentDataSources = None
        context.update({'getAllComponentDataSources': getAllComponentDataSources})

        # try:
        #     getAllDataFilters = {}
        #     for data_source in getAllComponentDataSources:
        #         data_source_filters = import_data_filter_options(data_source.data_source, data_source.data_filter_key, data_source.authorization_token)
        #         getAllDataFilters[data_source.id] = data_source_filters
        # except not getAllComponentDataSources:
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
        check_form_type = self.request.get_full_path()
        #TODO: Once refactoring is done, revisit whether checking form type still needed
        # if check_form_type.startswith('/confirgureabledashboard/map'):
        #     getCustomDashboard.component_map = form.cleaned_data['component_map']
        #     getCustomDashboard.save()
            # for position in getCustomDashboard.component_map:
            #     mapped_position = form.component_map.0
            #     if position.0 == mapped_position:
            #         position.1 == form.component_map.1
            #         mapped = true
            # if mapped != true:
            #     getCustomDashboard.component_map.append(form.component_map)
        # else:
        form.save()
        messages.success(self.request, 'Success, CustomDashboard Output Updated!')

        return self.render_to_response(self.get_context_data(form=form))


#TODO: build out code to import data filters for modal to select filters on wizard

def import_data_filter_options(data_url, column_filter, authorization_token):
  """
  For populating data filters in dropdown -- retrieve data_source using data_url
  """    
  filter_url = data_url
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
        getCustomDashboard = CustomDashboard.objects.all().get(id=self.kwargs['pk'])
        pk=self.kwargs['pk']
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
# {"1": "context_pane","2": "content_map","3": "bar_graph","4": "sidebar_events"}
# ===========================================
class DashboardThemeList(ListView):
    model = CustomDashboard
    template_name = 'configurabledashboard/themes/admin/list.html'

    def get(self, request, *args, **kwargs):
        getDashboardThemes = DashboardTheme.objects.all() 
        return render(request, self.template_name, {'getDashboardThemes': getDashboardThemes})


class DashboardThemeCreate(CreateView):
    model = DashboardTheme
    template_name = 'configurabledashboard/themes/admin/form.html'

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
        return super(DashboardThemeCreate, self).dispatch(request, *args, **kwargs)

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
        return super(DashboardThemeUpdate, self).dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(DashboardThemeUpdate, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        context.update({'pk': pk})
        getComplete = DashboardTheme.objects.get(id=self.kwargs['pk'])
        context.update({'getComplete': getComplete})
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
        ## retrieve program
        model = Program
        ## retrieve the countries the user has data access for
        countries = getCountry(request.user)
        dashboard_id = int(self.kwargs['pk'])
        
        getDashboardListComponents = DashboardComponent.objects.all().filter(componentset=dashboard_id)
            
        return render(request, self.template_name, {'getDashboardListComponents': getDashboardListComponents})


class DashboardComponentCreate(CreateView):
    model = DashboardComponent
    template_name = 'configurabledashboard/components/admin/form.html'

     # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(DashboardComponentCreate, self).get_form_kwargs()
        kwargs['request'] = self.request
        id = self.kwargs['id']
        return kwargs

    @method_decorator(group_excluded('ViewOnly', url='workflow/permission'))
    def dispatch(self, request, *args, **kwargs):
        try:
            guidance = FormGuidance.objects.get(form="DashboardComponent")
        except FormGuidance.DoesNotExist:
            guidance = None
        return super(DashboardComponentCreate, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = {
            'getCustomDashboard': CustomDashboard.objects.get(id=self.kwargs['id']),
            'getComponentDataSources': ComponentDataSource.objects.all(),
            }

    def get_context_data(self, **kwargs):
        context = super(DashboardComponentCreate, self).get_context_data(**kwargs)
        try:
            getCustomDashboard = CustomDashboard.objects.get(id=self.kwargs['id'])
        except CustomDashboard.DoesNotExist:
            getCustomDashboard = None
        context.update({'getCustomDashboard': getCustomDashboard})

        return context 

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        context = self.get_context_data()
        messages.success(self.request, 'Success, Component Created!')
        latestComponent = DashboardComponent.objects.latest('id')
        getCustomDashboard = CustomDashboard.objects.get(id=self.kwargs['id'])
        getCustomDashboard.components.add(latestComponent)
        return self.render_to_response(self.get_context_data(form=form))

    form_class = DashboardComponentCreateForm 


class DashboardComponentUpdate(UpdateView):
    model = DashboardComponent
    success_url = '/'

    def dispatch(self, request, *args, **kwargs):
        # try:
        #     guidance = FormGuidance.objects.get(form="DashboardComponentUpdate")
        # except FormGuidance.DoesNotExist:
        #     guidance = None
        return super(DashboardComponentUpdate, self).dispatch(request, *args, **kwargs)
    

    def get_context_data(self, **kwargs):
        context = super(DashboardComponentUpdate, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        context.update({'pk': pk})

        getComponentDataSources = []
        getComponentDataSources = ComponentDataSource.objects.all()
        context.update({'getComponentDataSources': getComponentDataSources})

        getDashboardComponent = DashboardComponent.objects.all().get(id=self.kwargs['pk'])
        context.update({'getDashboardComponent': getDashboardComponent})

        #for each component define the properties the component needs to have data mapped for by type
        #ideally this dictionary would be saved externally as a constant
        getComponentProperties = {
            'bar_graph':{'labels':'', 'data': '', 'colors':''}, 
            'doughnut': {'labels':'', 'data': '', 'colors':''}, 
            'line':{'labels':'', 'data': '', 'colors':''}, 
            'pie':{'labels':'', 'data': '', 'colors':''}, 
            'polar':{'labels':'', 'data': '', 'colors':''}, 
            'radar':{'labels':'', 'data': '', 'colors':''}, 
            'sidebar_gallery':{'photo_url':'', 'photo_titles':'', 'photo_captions':'', 'photo_dates':''}, 
            'content_map':{'latitude':'', 'longitude':'', 'location_name':'', 'description': '', 'region_link': '','region_name':''}, 
            'region_map':{'latitude':'', 'longitude':'', 'site_contact':'', 'location_name':'','description': ''}, 
            'sidebar_map':{'latitude':'', 'longitude':'', 'site_contact':'', 'location_name':'','description': ''}, 
            'context_pane':{}, 
            'sidebar_events':{}, 
            'sidebar_news':{},
            'sidebar_objectives':{}
        }
        context.update({'getComponentProperties': getComponentProperties})
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
        context = super(DashboardComponentDelete, self).get_context_data(**kwargs)
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
        getComponentDataSources = ComponentDataSource.objects.all()
            
        return render(request, self.template_name, {'getComponentDataSources': getComponentDataSources})

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
        return super(ComponentDataSourceCreate, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ComponentDataSourceCreate, self).get_context_data(**kwargs)
        return context

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid Form', fail_silently=False)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        context = self.get_context_data()
        messages.success(self.request, 'Success, Data Source Created!')
        return self.render_to_response(self.get_context_data(form=form))

    form_class = ComponentDataSourceCreateForm 


class ComponentDataSourceDetail(DetailView):
    model = ComponentDataSource
    template_name = 'configurabledashboard/datasource/detail.html'

    def get(self, request, *args, **kwargs):
        getComponentDataSources = ComponentDataSource.objects.all()
            
        return render(request, self.template_name, {'getComponentDataSources': getComponentDataSources})


class ComponentDataSourceUpdate(UpdateView):
    model = ComponentDataSource
    template_name = 'configurabledashboard/datasource/update_form.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            guidance = FormGuidance.objects.get(form="ComponentDataSource")
        except FormGuidance.DoesNotExist:
            guidance = None
        return super(ComponentDataSourceUpdate, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ComponentDataSourceUpdate, self).get_context_data(**kwargs)
        getComponentDataSource = ComponentDataSource.objects.all().get(id=self.kwargs['pk'])
        pk = self.kwargs['pk']
        context.update({'pk': pk})

        # get stuff
        return context

    # add the request to the kwargs
    def get_form_kwargs(self):
        kwargs = super(ComponentDataSourceUpdate, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    #get shared data from project agreement and pre-populate form with it
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
        context = super(ComponentDataSourceDelete, self).get_context_data(**kwargs)
        getDataSource = ComponentDataSource.objects.all().get(id=self.kwargs['pk'])
        pk=self.kwargs['pk']
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
