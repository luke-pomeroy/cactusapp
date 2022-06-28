from django.urls import path

from . import views
from . import api

urlpatterns = [
    path('', views.index, name='index'),
    path('maps/', views.map, name='map'),
    path('species/', views.SpeciesListView.as_view(), name='species'),
    path('species/scrape/', views.speciesfromurl, name='speciesfromurl'),
    path('species/<int:pk>', views.SpeciesDetailView.as_view(), name='species-detail'),
]

urlpatterns += [  
    path('species/create/', views.SpeciesCreate.as_view(), name='species-create'),
    path('species/update/', views.speciesgrid, name='species-update-all'),
    path('species/<int:pk>/location/', views.SpeciesAddLocationView.as_view(), name='species-add-location'),
    path('species/<int:pk>/location/success/', views.SpeciesAddLocationSuccView.as_view(), name='species-add-location-success'),
    path('species/<int:pk>/update/', views.SpeciesUpdate.as_view(), name='species-update'),
    path('species/<int:pk>/delete/', views.SpeciesDelete.as_view(), name='species-delete'),
    path('sources/', views.SourceListView.as_view(), name='sources'),
    path('sources/labels/', views.SourceLabelsView.as_view(), name='source-labels'),
    path('source/<int:pk>', views.SourceDetailView.as_view(), name='source-detail'),
    path('source/<int:pk>/label/', views.SourceLabelView.as_view(), name='source-label'),
    path('source/create/', views.SourceCreate.as_view(), name='source-create'),
    path('sources/update/', views.sourcegrid, name='sources-update'),
    path('source/<int:pk>/update/', views.SourceUpdate.as_view(), name='source-update'),
    path('source/<int:pk>/delete/', views.SourceDelete.as_view(), name='source-delete'),
    path('source/uuid/<uuid:uuid>', views.SourceUUIDView.as_view(), name='source-uuid'),

]

urlpatterns += [  
    path('therm/push/', views.add_therm, name='add-therm'),
    path('api/loggers/', api.AllLoggers.as_view(), name='api-loggers'),
    path('loggers/dashboard/', views.logger_dashboard, name='loggers-dashboard'),
    path('loggers/data/', views.LoggerDataListView.as_view(), name='loggers-data'),
]

