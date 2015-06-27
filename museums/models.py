from django.db import models
from localflavor.us.models import USStateField


class MuseumType(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.name


class Museum(models.Model):
    imls_id = models.CharField(max_length=255, default='')
    name = models.CharField(max_length=255, default='')
    url = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = USStateField(null=True, blank=True, db_index=True)
    zipcode = models.CharField(max_length=255, db_index=True)
    latitude = models.FloatField(default=0, null=True, blank=True)
    longitude = models.FloatField(default=0, null=True, blank=True)
    types = models.ForeignKey(MuseumType, db_index=True)

    def __unicode__(self):
        return "{0} ({1}, {2})".format(self.name, self.city, self.state)


class Search(models.Model):
    text = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.text[:100]


class GeoJSON(models.Model):

    name = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.url
