from django.contrib import admin
from .models import Museum, MuseumType, GeoJSON

admin.site.register(Museum)
admin.site.register(MuseumType)
admin.site.register(GeoJSON)
