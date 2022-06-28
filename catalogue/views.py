from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormMixin
from django.views.generic.list import ListView
from django_filters.views import FilterView
from django_tables2 import SingleTableView, SingleTableMixin, MultiTableMixin
from django_renderpdf.views import PDFView
from catalogue.models import *
from catalogue.forms import *
from catalogue.tables import *
from catalogue.filters import *
from catalogue.scrape import speciesscrape
import requests, re, json, uuid
import bisect

from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView

@login_required
def index(request):
    # Generate counts of some of the main objects
    num_species = Species.objects.all().count()
    num_sources = Source.objects.all().count()
    form = LocationForm()
    context = {
        'num_species': num_species,
        'num_sources': num_sources,
        'form':form,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

@login_required
def sourcegrid(request):
    queryset=Source.objects.all()
    forms_per_page = request.GET.get('per_page', 10)
    filter_set = SourceFilter(request.GET, queryset)
    paginator = Paginator(filter_set.qs, forms_per_page)

    if request.POST:
        formset = SourceListFormSet(request.POST)
        #save formset from the POST request
        if formset.is_valid():
            formset.save()
            current_page = request.GET.get('next_page', 1)
            page_object = paginator.page(current_page)
            formset = SourceListFormSet(queryset=page_object)
        else:
            # return current page with errors
            current_page = request.GET.get('page', 1)
            page_object = paginator.page(current_page)
    else: 
        # if GET request return current page
        current_page = request.GET.get('page', 1)
        page_object = paginator.page(current_page)
        formset = SourceListFormSet(queryset=page_object)

    page_numbers = paginator.get_elided_page_range(current_page, on_each_side=3, on_ends=2)
    page_object.ordered = True

    context = {
        'filter': filter_set,
        'formset': formset,
        'objects': page_object,
        'page_numbers': list(page_numbers),
        'current_page': current_page,
    }   

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'catalogue/source_list_update.html', context=context)

@login_required
def speciesgrid(request):
    queryset=Species.objects.all()
    forms_per_page = request.GET.get('per_page', 10)
    filter_set = SpeciesFilter(request.GET, queryset)
    paginator = Paginator(filter_set.qs, forms_per_page)

    if request.POST:
        formset = SpeciesListFormSet(request.POST)
        #save formset from the POST request
        if formset.is_valid():
            formset.save()
            current_page = request.GET.get('next_page', 1)
            page_object = paginator.page(current_page)
            formset = SpeciesListFormSet(queryset=page_object)
        else:
            # return current page with errors
            current_page = request.GET.get('page', 1)
            page_object = paginator.page(current_page)
    else: 
        # if GET request return current page
        current_page = request.GET.get('page', 1)
        page_object = paginator.page(current_page)
        formset = SpeciesListFormSet(queryset=page_object)

    page_numbers = paginator.get_elided_page_range(current_page, on_each_side=3, on_ends=2)
    page_object.ordered = True
    

    context = {
        'filter': filter_set,
        'formset': formset,
        'objects': page_object,
        'page_numbers': list(page_numbers),
        'current_page': current_page,
    }   

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'catalogue/species_list_update.html', context=context)

@login_required
def logger_dashboard(request):

    filter_set = LoggerDataFilter(request.GET)
    has_filter = any(field in request.GET for field in set(filter_set.get_fields()))
    datasets = []
    labels = []
    
    if has_filter:
        devices = filter_set.qs.order_by().values('device_id').distinct()
        backgroundColours = [
                                'rgba(255, 99, 132, 0.2)',
                                'rgba(54, 162, 235, 0.2)',
                                'rgba(255, 206, 86, 0.2)',
                                'rgba(75, 192, 192, 0.2)',
                                'rgba(153, 102, 255, 0.2)',
                                'rgba(255, 159, 64, 0.2)'
                            ]
        for index, device in enumerate(devices):
            print(device)
            readings = filter_set.qs.order_by('timestamp').filter(device_id=device['device_id'])
            device_data = []
            for reading in readings:
                if reading.timestamp.isoformat() not in labels:
                    labels.append(reading.timestamp.isoformat())
                data = {
                        "t": reading.timestamp.isoformat(),
                        "y": reading.temperature
                        }
                device_data.append(data)
            dataset = {
                "label": device['device_id'],
                "data": device_data,
                "backgroundColor": backgroundColours[index],

            }
            datasets.append(dataset)
        labels.sort()
        
    context = {
        'filter': filter_set,
        'datasets': datasets,
        'labels': labels,
    }
    return render(request, 'catalogue/logger_dashboard.html', context=context)

class LoggerDataListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    model = LoggerData
    paginate_by = 50
    table_class = LoggerDataTable
    template_name = 'catalogue/logger_data_list.html'
    filterset_class = LoggerDataFilter



@csrf_exempt
def add_therm(request):
    if 'application/json' in request.META['CONTENT_TYPE']:
        data = json.loads(request.body)

        if 'user' and 'pass' in data:
            user = authenticate(username=data['user'], password=data['pass'])
            if user is None:
                return HttpResponse(status=401)
        else:
            return HttpResponse(status=401)

        if 'humidity' and 'lux' in data:
            reading = LoggerData(device_id=data['device_id'], temperature=str(data['temperature']),
            humidity=str(data['humidity']), lux=str(data['lux']), timestamp=data['timestamp'])
        elif 'humidity' in data:
            reading = LoggerData(device_id=data['device_id'], temperature=str(data['temperature']),
            humidity=str(data['humidity']), timestamp=data['timestamp'])
        else:
            reading = LoggerData(device_id=data['device_id'], temperature=str(data['temperature']),
            timestamp=data['timestamp'])
        reading.save()
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=400)

@login_required
def map(request):
    
    locations = [
        [l.name, str(l.position.latitude), str(l.position.longitude), i]
        for i, l in enumerate(Location.objects.all())
    ]

    context = {
        'locations': json.dumps(locations),
    }

    return render(request, 'catalogue/map_test.html', context=context )

@login_required
def speciesfromurl(request):
    
    if request.POST:
        form = ScrapeForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['scrapeURL']
            new_species = speciesscrape(url)
            return HttpResponseRedirect(reverse('species-detail', args = [new_species.pk]))
    else:
        form = ScrapeForm()
        
    url = 'none'
    soup = ''
    results = []
    species = ''
    family = ''
    main_author = ''
    main_subheader = ''
    photos = ''

    context = {
        'form': form,
        'scrapeVAR': url,
        'soup': soup,
        'terms': results,
        'species': species,
        'family' :family,
        'author' : main_author,
        'subheader' : main_subheader,
        'photos': photos,
    }

    return render(request, 'catalogue/scrape.html', context=context)

class SpeciesListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    model = Species
    paginate_by = 10
    table_class = SpeciesTable
    template_name = 'catalogue/species_list.html'
    filterset_class = SpeciesFilter

class SpeciesDetailView(LoginRequiredMixin, generic.DetailView):
    model = Species
    paginate_by = 1

    def get_context_data(self, **kwargs):
        data = super(SpeciesDetailView, self).get_context_data(**kwargs)
        locations = [
        [l.name, str(l.position.latitude), str(l.position.longitude), i]
        for i, l in enumerate(Location.objects.filter(species=self.kwargs['pk']))
        ]
        data['locations'] = json.dumps(locations)
        species = self.object
        data['pagination'] = {
            'next': Species.objects.filter(scientific_name__gt=species.scientific_name).order_by('scientific_name').first(),
            'prev': Species.objects.filter(scientific_name__lt=species.scientific_name).order_by('scientific_name').last(),
        }
        print(data['pagination'])
        if self.request.POST:
            data['form'] = ScrapeForm(self.request.POST)
        else:
            data['form'] = ScrapeForm()

        return data

class SpeciesAddLocationView(LoginRequiredMixin, CreateView):
    model = Location
    template_name = 'catalogue/species_add_location.html'
    form_class = SpeciesLocationForm

    def form_valid(self, form):
        context = self.get_context_data()
        with transaction.atomic():
            form.instance.species = context['species']
            self.object = form.save()
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        """Pass some extra context to the template."""
        context = super().get_context_data(*args, **kwargs)

        context['species'] = Species.objects.filter(
            id=self.kwargs['pk'],
        ).first()
        return context

    def get_success_url(self):
        return reverse_lazy('species-add-location-success', kwargs={'pk': self.object.species.pk})
        

class SpeciesAddLocationSuccView(LoginRequiredMixin, generic.DetailView):
    model = Species
    template_name = 'catalogue/species_add_location_success.html'

class SpeciesCreate(LoginRequiredMixin, CreateView):
    model = Species
    template_name = 'catalogue/species_create.html'
    form_class = SpeciesForm
    success_url = None

    def get_context_data(self, **kwargs):
        data = super(SpeciesCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['descriptions'] = SpeciesDescriptionFormSet(self.request.POST)
            data['common_names'] = CommonNameFormSet(self.request.POST)
            data['locations'] = LocationFormSet(self.request.POST)
            data['photos'] = PhotoFormSet(self.request.POST, self.request.FILES)
        else:
            data['descriptions'] = SpeciesDescriptionFormSet()
            data['common_names'] = CommonNameFormSet()
            data['locations'] = LocationFormSet()
            data['photos'] = PhotoFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        descriptions = context['descriptions']
        common_names = context['common_names']
        photos = context['photos']
        locations = context['locations']
        with transaction.atomic():
            form.instance.created_by = self.request.user
            self.object = form.save()
            if descriptions.is_valid():
                descriptions.instance = self.object
                descriptions.save()
            if common_names.is_valid():
                common_names.instance = self.object
                common_names.save()
            if locations.is_valid():
                locations.instance = self.object
                locations.save()
            if photos.is_valid():
                photos.instance = self.object
                for index, f in enumerate(photos.cleaned_data):
                    try:
                        photo = Photo(content_object=self.object, image=f['image'], 
                                caption=f['caption'],image_url=f['image_url'], order=index)
                        photo.save()
                    except Exception as e:
                        break
        return super(SpeciesCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('species-detail', kwargs={'pk': self.object.pk})

class SpeciesUpdate(LoginRequiredMixin, UpdateView):
    model = Species
    template_name = 'catalogue/species_create.html'
    form_class = SpeciesForm
    success_url = None

    def get_context_data(self, **kwargs):
        data = super(SpeciesUpdate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['descriptions'] = SpeciesDescriptionFormSet(self.request.POST, instance=self.object)
            data['common_names'] = CommonNameFormSet(self.request.POST, instance=self.object)
            data['photos'] = PhotoFormSet(self.request.POST, self.request.FILES, instance=self.object)
            data['locations'] = LocationFormSet(self.request.POST, instance=self.object)

        else:
            data['descriptions'] = SpeciesDescriptionFormSet(instance=self.object)
            data['common_names'] = CommonNameFormSet(instance=self.object)
            data['photos'] = PhotoFormSet(instance=self.object)
            data['locations'] = LocationFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        descriptions = context['descriptions']
        common_names = context['common_names']
        photos = context['photos']
        locations = context['locations']
        with transaction.atomic():
            form.instance.created_by = self.request.user
            self.object = form.save()
            if descriptions.is_valid():
                descriptions.instance = self.object
                descriptions.save()
            if common_names.is_valid():
                common_names.instance = self.object
                common_names.save()
            if locations.is_valid():
                locations.instance = self.object
                locations.save()
                print(locations.deleted_objects)

                for location in locations.deleted_objects:
                    if location.id:
                        location.delete()
            if photos.is_valid():
                photos.instance = self.object
                photos.save()
        return super(SpeciesUpdate, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('species-detail', kwargs={'pk': self.object.pk})

class SpeciesDelete(LoginRequiredMixin, DeleteView):
    model = Species
    def get_success_url(self):

        return reverse_lazy('species', kwargs={})

class SourceDetailView(LoginRequiredMixin, FormMixin, generic.DetailView):
    model = Source
    form_class = ScrapeForm

    def get_context_data(self, **kwargs):
        data = super(SourceDetailView, self).get_context_data(**kwargs)
        source = self.object
        data['pagination'] = {
            'next': Source.objects.filter(id__gt=source.id).order_by('name').first(),
            'prev': Source.objects.filter(id__lt=source.id).order_by('name').last(),
        }

        return data

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            url = form.cleaned_data['scrapeURL']
            existing_species = Species.objects.filter(url=url)
            if existing_species:
                self.object.species = existing_species.first()
                self.object.save()
            else:
                new_species = speciesscrape(url)
                self.object.species = new_species
                self.object.save()
            return HttpResponseRedirect(reverse('source-detail', args = [self.object.pk]))

class SourceLabelView(LoginRequiredMixin, generic.DetailView):
    model = Source
    """Generate labels for some Sources

    A PDFView behaves pretty much like a TemplateView, so you can treat it as such.
    """
    template_name = 'catalogue/labels.html'
    
    def get_context_data(self, *args, **kwargs):
        """Pass some extra context to the template."""
        context = super().get_context_data(*args, **kwargs)

        context['sources'] = Source.objects.filter(
            id=14
        )
        return context


class SourceLabelsView(LoginRequiredMixin, PDFView):
    template_name = 'catalogue/labels.html'

    def get_context_data(self, *args, **kwargs):
        """Pass some extra context to the template."""
        context = super().get_context_data(*args, **kwargs)

        context['sources'] = Source.objects.filter(
            date_sown=self.request.GET.get('date_sown',''),
        )
        return context

class SourceListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    model = Source
    paginate_by = 12
    table_class = SourceTable
    template_name = 'catalogue/source_list.html'
    filterset_class = SourceFilter

    def get_context_data(self, **kwargs):
        data = super(SourceListView, self).get_context_data(**kwargs)
        return data

class SourceListEditView(LoginRequiredMixin, FormMixin, FilterView):
    template_name = 'catalogue/source_list_update.html'
    form_class = SourceListFormSet
    filterset_class = SourceFilter

class SourceCreate(LoginRequiredMixin, CreateView):
    model = Source
    template_name = 'catalogue/source_create.html'
    form_class = SourceForm
    success_url = None

    def get_context_data(self, **kwargs):
        data = super(SourceCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['photos'] = PhotoFormSet(self.request.POST, self.request.FILES)
        else:
            data['photos'] = PhotoFormSet()
            
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        photos = context['photos']
        with transaction.atomic():
            form.instance.created_by = self.request.user
            self.object = form.save()
            if photos.is_valid():
                photos.instance = self.object
                for index, f in enumerate(photos.cleaned_data):
                    try:
                        photo = Photo(content_object=self.object, image=f['image'], 
                                caption=f['caption'],image_url=f['image_url'], order=index)
                        photo.save()
                    except Exception as e:
                        break
        return super(SourceCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('source-detail', kwargs={'pk': self.object.pk})

class SourceUpdate(LoginRequiredMixin, UpdateView):
    model = Source
    template_name = 'catalogue/source_create.html'
    form_class = SourceForm
    success_url = None

    def get_context_data(self, **kwargs):
        data = super(SourceUpdate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['photos'] = PhotoFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            data['photos'] = PhotoFormSet(instance=self.object)

        return data

    def form_valid(self, form):
        context = self.get_context_data()
        photos = context['photos']
        with transaction.atomic():
            form.instance.created_by = self.request.user
            self.object = form.save()
            if photos.is_valid():
                photos.instance = self.object
                photos.save()
                #for index, f in enumerate(photos.cleaned_data):
                #    try:
                #        photo = Photo(content_object=self.object, image=f['image'], 
                #                caption=f['caption'],image_url=f['image_url'], order=index)
                #        photo.save()
                #    except Exception as e:
                #        break
        return super(SourceUpdate, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('source-detail', kwargs={'pk': self.object.pk})

class SourceDelete(LoginRequiredMixin, DeleteView):
    model = Source

class SourceUUIDView(LoginRequiredMixin, generic.DetailView):
    model = Source
    slug_url_kwarg = 'uuid'
    slug_field = 'uuid'
