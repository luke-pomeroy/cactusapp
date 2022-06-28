from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from djangoyearlessdate.models import YearlessDateField
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse # Used to generate URLs by reversing the URL patterns
from django.contrib.auth.models import User
from django.core import files
import django_filters
import imghdr # Used to validate images
import urllib # Used to download images
import requests, datetime
import tempfile
import io
from PIL import Image # Holds downloaded image and verifies it
import copy # Copies instances of Image
from datetime import date
import uuid # Required for unique uuids
from django.utils import timezone

from versatileimagefield.fields import VersatileImageField, PPOIField
from geoposition.fields import GeopositionField

class Photo(models.Model):
    image = VersatileImageField(
        'Image',
        upload_to='images/',
        width_field='width',
        height_field='height',
        blank=True,
        null=True
    )
    caption = models.CharField(
        'Caption',
        max_length=80
    )
    height = models.PositiveIntegerField(
        'Image Height',
        blank=True,
        null=True
    )
    width = models.PositiveIntegerField(
        'Image Width',
        blank=True,
        null=True
    )
    created = models.DateTimeField(editable=False)
    image_url = models.URLField(null=True, blank=True)
    order = models.PositiveIntegerField(default=1)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        if (self.image_url != None):
            url = self.image_url
            image_file = download_image(url) # See function definition below
            try:
                filename = urllib.parse.urlparse(url).path.split('/')[-1]
                self.image.save(filename, image_file, save=False) # Set save=False otherwise you will have a looping save method
            except Exception as e:
                print ("Error trying to save model: saving image failed: " + str(e))
                pass
        super(Photo, self).save(*args, **kwargs) # We've gotten the image into the ImageField above...now we actually need to save it. We've redefined the save method for Product, so super *should* get the parent of class Product, models.Model and then run IT'S save method, which will save the Product like normal
        
    def __str__(self):
        return f'{self.id} : {self.image_url}  -  ({self.caption})'

def download_image(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0'} # More likely to get a response if server thinks you're a browser
    response = requests.get(url, stream=True)    
    # Create a temporary file
    lf = tempfile.NamedTemporaryFile()
    # Read the streamed image in sections
    for block in response.iter_content(1024 * 8):
        # If no more file then stop
        if not block:
            break
        # Write image block to temporary file
        lf.write(block)
    img = files.File(lf)

    return img
        
def valid_img(img):
    type = img.format
    if type in ('GIF', 'JPEG', 'JPG', 'PNG'):
        try:
            img.verify()
            return True
        except:
            return False
    else: return False

DIFFICULTY_LEVELS = [
        ('VERY_EASY', 'Very easy'),
        ('EASY', 'Easy'),
        ('AVERAGE', 'Average'),
        ('SOME_DIFFICULTY', 'Some difficulty'),
        ('DIFFICULT', 'Difficult'),
        ('VERY_DIFFICULT', 'Very difficult'),
    ]    

class Species(models.Model):
    scientific_name = models.CharField(max_length=200, help_text='Enter the scientific name for this species')
    family = models.CharField(max_length=200, null=True, blank=True)
    author = models.CharField(max_length=200, null=True, blank=True)
    source = models.CharField(max_length=200, null=True, blank=True)
    genus = models.CharField(max_length=200, null=True, blank=True)
    subgenus = models.CharField(max_length=200, null=True, blank=True)
    specific_epithet = models.CharField(max_length=200, null=True, blank=True)
    origin = models.CharField(max_length=200, null=True, blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='AVERAGE')
    growing_season_start = YearlessDateField(null=True, blank=True)
    growing_season_end = YearlessDateField(null=True, blank=True)
    min_temp_c = models.FloatField(null=True, blank=True)
    max_temp_c = models.FloatField(null=True, blank=True)
    light = models.CharField(max_length=200, null=True, blank=True)
    watering = models.CharField(max_length=200, null=True, blank=True)
    humidity = models.CharField(max_length=200, null=True, blank=True)
    substrate = models.CharField(max_length=200, null=True, blank=True)
    url = models.URLField(max_length=200, null=True, blank=True)
    photos = GenericRelation(Photo, related_query_name='species')

    def __str__(self):
        return self.scientific_name
    
    def get_absolute_url(self):
        return reverse('species-detail', args=[str(self.id)])
    
    def primary_image(self):
        primary = Photo.objects.filter(species=self).first()
        return primary.image.crop["300x300"]

    def location_count(self):
        location_count = Location.objects.filter(species=self).count()
        return location_count
    
    def primary(self):
        primary = Photo.objects.filter(species=self).first()
        return primary

    class Meta:
        verbose_name_plural = "Species"
        ordering = ['scientific_name']

class Location(models.Model):
    name = models.CharField(max_length=100)
    position = GeopositionField()
    species = models.ForeignKey(Species, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class SpeciesDescription(models.Model):
    description = models.CharField(max_length=4000)
    descript_type = models.CharField(max_length=100)
    descript_group = models.CharField(max_length=100, null=True, blank=True)
    order = models.PositiveIntegerField(default=1)
    species = models.ForeignKey('Species', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.descript_type}: {self.description}'

class CommonName(models.Model):
    common_name = models.CharField(max_length=200)
    meaning = models.CharField(max_length=500)
    species = models.ForeignKey('Species', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.common_name

STATUSES = [
        ('PENDING', 'Pending'),
        ('SOWN', 'Sown'),
        ('ACTIVE', 'Active'),
        ('NO_RESULTS', 'No results'),
        ('NON-ARRIVAL', 'Did not arrive'),
    ]

class SoilType(models.Model):
    composition = models.CharField(max_length=300)
    treatment = models.CharField(max_length=300)
    
    def __str__(self):
        return self.composition

class Source(models.Model):
    name = models.CharField(max_length=200)
    uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, unique=True, editable=False)
    species = models.ForeignKey('Species', on_delete=models.SET_NULL, null=True, blank=True, related_name='sources') 
    seed_count = models.IntegerField()
    obtained_from = models.CharField(max_length=100)
    purchase_date = models.DateField(null=True, blank=True)
    supplier_reference = models.CharField(max_length=50)
    note = models.CharField(max_length=1000, null=True, blank=True)
    cost = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    date_sown = models.DateField(null=True, blank=True, help_text='Date acquired, or date sown if from seed.')
    sowing_method = models.CharField(max_length=300, null=True, blank=True)
    ten_day_count = models.IntegerField(null=True, blank=True)
    end_count = models.IntegerField(null=True, blank=True)
    soil_type = models.ForeignKey('SoilType', on_delete=models.SET_NULL, null=True, blank=True, related_name='sources') 
    photos = GenericRelation(Photo, related_query_name='source')

    status = models.CharField(max_length=20, choices=STATUSES, default='PENDING')

    def get_absolute_url(self):
        return reverse('source-detail', args=[str(self.id)])

    def primary_image(self):
        primary = Photo.objects.filter(source=self).order_by('-created').first()
        return primary.image.crop["300x300"]

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class F(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=STATUSES)
    class Meta:
        model = Source
        fields = ['status']

class LoggerData(models.Model):
    device_id = models.CharField(max_length=100)
    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    lux = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField()

    def nearest_timestamp(self, roundTo=60*5):
        """Round a datetime object to any time lapse in seconds
        dt : datetime.datetime object.
        roundTo : Closest number of seconds to round to, default 1 minute.
        """
        dt = self.timestamp
        seconds = (dt.replace(tzinfo=None) - dt.min).seconds
        rounding = (seconds+roundTo/2) // roundTo * roundTo
        print(dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond))
        return dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond)

    class Meta:
        ordering = ['device_id', '-timestamp']
    