import datetime
from fractions import Fraction

from django import forms
from catalogue.models import *
from django.forms.models import inlineformset_factory, modelformset_factory
from django.forms import formset_factory
from django.contrib.contenttypes.forms import generic_inlineformset_factory, BaseGenericInlineFormSet

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Div, HTML, ButtonHolder, Submit
from catalogue.custom_layout_object import *
from versatileimagefield.fields import VersatileImageField
from geoposition.fields import GeopositionField 
from geoposition.widgets import GeopositionWidget
from djangoyearlessdate.forms import YearlessDateSelect

def validate_scrapeURL(value):
    if 'llifle.com' not in value:
        raise ValidationError('The URL entered must be for llifle.com. You entered: %(value)s',
                              code='invalid',
                              params={'value': value})

class ScrapeForm(forms.Form):
    scrapeURL = forms.CharField(label='Enter scrape URL', max_length=200, validators=[validate_scrapeURL])

class SpeciesDescriptionForm(forms.ModelForm):

    class Meta:
        model = SpeciesDescription
        exclude = ()

class CommonNameForm(forms.ModelForm):

    class Meta:
        model = CommonName
        exclude = ()

class SoilTypeForm(forms.ModelForm):

    class Meta:
        model = SoilType
        exclude = ()

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        exclude = ()

class LocationForm(forms.ModelForm):
    name = forms.CharField()
    position = GeopositionField

    class Meta:
        model = Location
        exclude = ('species',)

    def __init__(self, *args, **kwargs):
        super(LocationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True

PhotoFormSet = generic_inlineformset_factory(
    Photo, form=PhotoForm, formset=BaseGenericInlineFormSet,
    fields=['image', 'caption','order', 'image_url'], extra=1, can_delete=True
    )

LocationFormSet = inlineformset_factory(
    Species, Location, form=LocationForm,
    fields=['name', 'position'], extra=1, can_delete=True
    )

SpeciesDescriptionFormSet = inlineformset_factory(
    Species, SpeciesDescription, form=SpeciesDescriptionForm,
    fields=['descript_type', 'description'], extra=1, can_delete=True
    )

CommonNameFormSet = inlineformset_factory(
    Species, CommonName, form=CommonNameForm,
    fields=['common_name', 'meaning'], extra=1, can_delete=True
    )

class SpeciesForm(forms.ModelForm):
    class Meta:
        model = Species
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(SpeciesForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.helper.layout = Layout(
            Div(
                Field('scientific_name'),
                Fieldset('Add locations',
                    Formset('locations')),
                Fieldset('Add images',
                    Formset('photos')),
                Fieldset('Add common names',
                    Formset('common_names')),
                Field('family'),
                Field('genus'),
                Field('subgenus'),
                Field('specific_epithet'),
                Field('difficulty'),
                Field('growing_season_start'),
                Field('growing_season_end'),
                Field('min_temp_c'),
                Field('max_temp_c'),
                Field('light'),
                Field('watering'),
                Field('humidity'),
                Field('substrate'),
                Field('url'),
                Fieldset('Add descriptions',
                    Formset('descriptions')),
                HTML("<br>"),
                ButtonHolder(Submit('submit', 'save')),
                )
            )

class SpeciesLocationForm(forms.ModelForm):

    class Meta:
        model = Location
        exclude = ('species',)

    def __init__(self, *args, **kwargs):
        super(SpeciesLocationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))
        self.helper.form_method = 'POST'


class SourceListForm(forms.ModelForm):

    name = forms.CharField(disabled=True)
    supplier_reference = forms.CharField(disabled=True)
    date_sown = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))  
    status = forms.ChoiceField(choices = STATUSES)
    seed_count = forms.IntegerField()
    ten_day_count = forms.IntegerField()
    end_count = forms.IntegerField()
    class Meta:
        model = Source
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(SourceListForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form form-inline'
        self.helper.layout = Layout(
            Div(
                Field('name'),
                Field('supplier_reference'),
                Field('date_sown'),
                Field('status'),
                Field('seed_count'),
                Field('ten_day_count'),
                Field('end_count'),
                HTML("<br>"),
                )
            )

class SpeciesListFormGrid(forms.ModelForm):
    scientific_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'style':'min-width: 15em'}))
    genus = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'min-width: 15em'}))
    specific_epithet = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'min-width: 15em'}))
    author = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'min-width: 15em'}))
    difficulty = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'min-width: 15em'}))
    growing_season_start = YearlessDateSelect
    growing_season_end = YearlessDateSelect
    min_temp_c = forms.IntegerField(required=False)
    max_temp_c = forms.IntegerField(required=False)
    light = forms.IntegerField(required=False)
    watering = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'min-width: 15em'}))
    humidity = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'min-width: 15em'}))
    substrate = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'min-width: 15em'}))

    class Meta:
        model = Species
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(SpeciesListFormGrid, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
                Field('scientific_name'),
                Field('genus'),
                Field('specific_epithet'),
                Field('author'),
                Field('difficulty'),
                Field('growing_season_start'),
                Field('growing_season_end'),
                Field('min_temp_c'),
                Field('max_temp_c'),
                Field('light'),
                Field('watering'),
                Field('humidity'),
                Field('substrate'),
        )

SpeciesListFormSet = modelformset_factory(
    Species, form=SpeciesListFormGrid, fields=['scientific_name', 'genus', 'specific_epithet', 'author'], extra=0
    )

class SourceListFormGrid(forms.ModelForm):
    name = forms.CharField(disabled=True, widget=forms.TextInput(attrs={'style':'min-width: 15em'}))
    supplier_reference = forms.CharField(disabled=True, widget=forms.TextInput(attrs={'style':'min-width: 15em'}))
    date_sown = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date', 'style':'max-width: 12em'}))  
    status = forms.ChoiceField(choices = STATUSES, widget=forms.Select(choices=STATUSES, attrs={'type': 'choices', 'style':'min-width: 10em'}))
    seed_count = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'style':'max-width:7em, min-width: 7em'}))
    ten_day_count = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'style':'max-width: 7em, min-width: 7em'}))
    end_count = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'style':'max-width: 7em, min-width: 7em'}))
    class Meta:
        model = Source
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(SourceListFormGrid, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
                Field('name'),
                Field('supplier_reference'),
                Field('date_sown'),
                Field('status'),
                Field('seed_count'),
                Field('ten_day_count'),
                Field('end_count'),

        )

SourceListFormSet = modelformset_factory(
    Source, form=SourceListFormGrid, fields=['name', 'supplier_reference', 'date_sown', 'status', 'seed_count', 'ten_day_count', 'end_count'], extra=0
    )

class SourceForm(forms.ModelForm):
    date_sown = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))  
    purchase_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))   
    
    class Meta:
        model = Source
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(SourceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.helper.layout = Layout(
            Div(
                Field('name'),
                Field('species'),
                Field('seed_count'),
                Field('obtained_from'),
                Field('purchase_date'),
                Field('supplier_reference'),
                Field('cost'),
                Field('note'),
                Field('status'),
                Field('date_sown'),
                Field('sowing_method'),
                Field('ten_day_count'),
                Field('soil_type'),
                Field('end_count'),
                Fieldset('Supplier images',
                    Formset('photos')),
                HTML("<br>"),
                ButtonHolder(Submit('submit', 'save')),
                )
            )

