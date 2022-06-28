import django_tables2 as tables
from .models import *
from django.utils.safestring import mark_safe
from django.utils.html import escape, format_html
from django_tables2.utils import A  # alias for Accessor

class ImageColumn(tables.Column):
        def render(self, value):
            return format_html(
               '<img src="{url}" class="fav" height="150px", width="150px">',
                url=value
                )

class SpeciesTable(tables.Table):
    primary_image = ImageColumn()
    scientific_name = tables.LinkColumn("species-detail", args=[A("pk")])
    genus = tables.Column()
    specific_epithet = tables.Column()
    author = tables.Column()
    sources = tables.ManyToManyColumn(accessor="sources", separator="; ", linkify_item=True, verbose_name="Sources")
    location_count = tables.Column(verbose_name='Locations')
    difficulty = tables.Column()
    growing_season_start = tables.Column()
    growing_season_end = tables.Column()
    min_temp_c = tables.Column()
    max_temp_c = tables.Column()
    light = tables.Column()
    watering = tables.Column()
    humidity = tables.Column()
    substrate = tables.Column()
    url = tables.Column(linkify=True)

    class Meta:
        Model = Species
        template_name = 'catalogue/data-table-bootstrap.html'

class SourceTable(tables.Table):
    species_image = ImageColumn(accessor="species__primary_image")
    name = tables.LinkColumn("source-detail", args=[A("pk")])
    supplier_reference = tables.Column()
    species = tables.Column(linkify=True)
    status = tables.Column()
    date_sown = tables.Column()
    obtained_from = tables.Column() 
    purchase_date = tables.Column()
    seed_count = tables.Column()
    end_count = tables.Column()
    note = tables.Column()
    uuid = tables.Column()

    class Meta:
        Model = Source
        template_name = 'catalogue/data-table-bootstrap.html'

class LoggerDataTable(tables.Table):
    device_id = tables.Column()
    temperature = tables.Column()
    humidity = tables.Column()
    lux = tables.Column()
    timestamp = tables.Column()
    nearest_timestamp = tables.Column(accessor='nearest_timestamp')

    class Meta:
        Model = LoggerData
        template_name = 'catalogue/data-table-bootstrap.html'