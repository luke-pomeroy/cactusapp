# Cactusapp

I created this app to maintain a record of my cacti seed sowings, recording information relating to each species, and to provide an API endpoint for receiving environmental data readings from Arduino data loggers via HTTPS. This app is hosted on an Oracle Cloud E2.1 micro instance.

Cactusapp app utilises several Django packages including:
- [*django-crispy-forms*](https://github.com/django-crispy-forms/django-crispy-forms) for controlling the rendering of Django forms.
- [*django-tables2*](https://github.com/jieter/django-tables2) for providing data tables of species and sources.
- [*django-filter*](https://github.com/carltongibson/django-filter) for filtering Django querysets based on a model's fields.
- [*django-versatileimagefield*](https://github.com/respondcreate/django-versatileimagefield) for providing dynamic image derivatives.
- [*django-import-export*](https://github.com/django-import-export/django-import-export) for importing lists of seeds from a spreadsheet or csv file.
- [*django-geoposition*](https://github.com/whyspark/django-geoposition) for displaying pins on a Google Map for species localities.
- [*django-chartjs*](https://github.com/peopledoc/django-chartjs) for displaying environmental data readings in a graph.
- [*django-renderpdf*](https://github.com/WhyNotHugo/django-renderpdf) for rendering PDF Zebra labels for Sources.

Cactusapp also utilises the [*Beautiful Soup*](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) Python library to scrape web pages on [*Llifle.com*](llifle.com), an excellent encyclopedia of living forms with a wealth of information relating to cacti and succulent species.

Some images of Cactusapp:

![Species List Example](static/catalogue/SpeciesList.JPG?raw=true "Species List Example")

![Species Gallery Example](static/catalogue/SpeciesExampleGallery.JPG?raw=true "Species Gallery Example")

![Species Detail Example](static/catalogue/SpeciesExample.JPG?raw=true "Species Detail Example")

![Species Mass Update Example](static/catalogue/UpdateAllSpecies.JPG?raw=true "Species Mass Update Example")

![Source List Example](static/catalogue/SpeciesList.JPG?raw=true "Source List Example")

![Species Beautiful Soup Scrape Example](static/catalogue/Scrape.JPG?raw=true "Species Beautiful Soup Scrape Example")

![Zebra Labels from Sources Example](static/catalogue/ZebraLabels.JPG?raw=true "Zebra Labels from Sources Example")

## ToDo
- [ ] Add model to represent each individual plant with relationships to Species and Sources
- [ ] Add feature for taking images of individual plants via web app.
- [ ] Show temperature *and humidity* on Chartjs graph (currently is just temperature).


