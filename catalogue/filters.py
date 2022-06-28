import django_filters
from catalogue.models import *
from django import forms

def get_choices(model, field):
    choices = []
    for k in model.objects.order_by(field).values_list(field).distinct():
        choices.append((k[0], k[0]))
    return choices

class SpeciesFilter(django_filters.FilterSet):
    scientific_name = django_filters.CharFilter(lookup_expr='icontains', label='Scientific Name')
    family = django_filters.AllValuesFilter(label='Family')   
    genus = django_filters.AllValuesFilter()
    author = django_filters.AllValuesFilter()
    class Meta:
        model = Species
        exclude = ()
        fields = ['scientific_name', 'family']

class SourceFilter(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['obtained_from'].extra['choices'] = get_choices(Source, 'obtained_from')
        self.filters['purchase_date'].extra['choices'] = get_choices(Source, 'purchase_date')
        self.filters['date_sown'].extra['choices'] = get_choices(Source, 'date_sown')

    name = django_filters.CharFilter(lookup_expr='icontains')
    obtained_from = django_filters.MultipleChoiceFilter(choices=get_choices(Source, 'obtained_from'))
    purchase_date = django_filters.MultipleChoiceFilter(choices=get_choices(Source, 'purchase_date'))
    date_sown = django_filters.MultipleChoiceFilter(choices=get_choices(Source, 'date_sown'))

    status = django_filters.MultipleChoiceFilter(choices=STATUSES)
    
    class Meta:
        model = Source
        exclude = ()
        fields = ['name', 'purchase_date', 'obtained_from', 'status', 'date_sown']

class LoggerDataFilter(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['device_id'].extra['choices'] = get_choices(LoggerData, 'device_id')

    device_id = django_filters.MultipleChoiceFilter(label='Device', choices=get_choices(LoggerData, 'device_id'))
    timestamp = django_filters.DateRangeFilter(label='Period')
    start_date = django_filters.DateFilter(label='From date', field_name='timestamp',lookup_expr=('lt'),widget=forms.TextInput(attrs={'type': 'date', 'style':'max-width: 12em'})) 
    end_date = django_filters.DateFilter(label='To date', field_name='timestamp',lookup_expr=('gt'), widget=forms.TextInput(attrs={'type': 'date', 'style':'max-width: 12em'}))

    class Meta:
        model = LoggerData
        exclude = ()
        fields = ['device_id', 'timestamp']