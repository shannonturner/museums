from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.contrib import messages
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

from geopy.distance import vincenty
from geopy.geocoders import GoogleV3

from localflavor.us.us_states import STATES_NORMALIZED, US_STATES

import hashlib
import json

from .models import Museum, MuseumType, Search, GeoJSON

RADIUS = 100  # miles
PATH_PREFIX = '/home/sturner/apps/shannonvturner-com/museums_geojson/'
# PATH_PREFIX = ''

class HomeView(TemplateView):

    template_name = 'index.html'
    geolocator = GoogleV3()
    states_and_abbrevs = ['alabama', 'al', 'alaska', 'ak', 'arizona', 'az', 'arkansas', 'ar', 'california', 'ca', 'colorado', 'co', 'connecticut', 'ct', 'delaware', 'de', 'district of columbia', 'dc', 'florida', 'fl', 'georgia', 'ga', 'hawaii', 'hi', 'idaho', 'id', 'illinois', 'il', 'indiana', 'in', 'iowa', 'ia', 'kansas', 'ks', 'kentucky', 'ky', 'louisiana', 'la', 'maine', 'me', 'maryland', 'md', 'massachusetts', 'ma', 'michigan', 'mi', 'minnesota', 'mn', 'mississippi', 'ms', 'missouri', 'mo', 'montana', 'mt', 'nebraska', 'ne', 'nevada', 'nv', 'new hampshire', 'nh', 'new jersey', 'nj', 'new mexico', 'nm', 'new york', 'ny', 'north carolina', 'nc', 'north dakota', 'nd', 'ohio', 'oh', 'oklahoma', 'ok', 'oregon', 'or', 'pennsylvania', 'pa', 'rhode island', 'ri', 'south carolina', 'sc', 'south dakota', 'sd', 'tennessee', 'tn', 'texas', 'tx', 'utah', 'ut', 'vermont', 'vt', 'virginia', 'va', 'washington', 'wa', 'west virginia', 'wv', 'wisconsin', 'wi', 'wyoming', 'wy']

    def get(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        category = request.POST.get('category')
        location = request.POST.get('location')

        context = self.get_context_data(**kwargs)
        context['map'] = True

        if category:
            search = Search(**{'text': 'Category: {0}'.format(category)})
            search.save()
            museums = Museum.objects.filter(types__code=category)
            geojson = self.get_geojson(**{'name': category, 'museums': museums})
            context["jsonfile"] = category
        elif location:
            search = Search(**{'text': location})
            search.save()
            # Inputs: If just a state/abbrev given, show all items for that state only, no radius
            # Otherwise, geocode the result, run the vicenty distance
            if location.lower() in self.states_and_abbrevs:
                if len(location) != 2:
                    location = STATES_NORMALIZED.get(location.lower())
                context["jsonfile"] = location
                # TEMPORARY: EXCLUDE 11K GENERAL MUSEUMS FOR NOW -- Can always add them back later
                museums = Museum.objects.filter(state=location).exclude(types__code='GMU')
                if museums.count() > 0:
                    geojson = self.get_geojson(**{'name': location, 'museums': museums})
                    # By this point, location is always a two-letter abbreviation
                    address, (latitude, longitude) = self.geolocator.geocode(''.join([state_tuple[1] for state_tuple in US_STATES if state_tuple[0] == location]))
            else:
                try:
                    museums = []
                    address, (latitude, longitude) = self.geolocator.geocode(location)
                except Exception:
                    context["jsonfile"] = ""
                else:
                    if latitude and longitude:
                        all_museums = Museum.objects.exclude(types__code='GMU')

                        for museum in all_museums:
                            dist = vincenty(
                                (museum.latitude, museum.longitude), 
                                (latitude, longitude)
                            ).miles

                            if dist <= RADIUS:
                                museums.append(museum)

                        context["jsonfile"] = hashlib.sha256(location).hexdigest()[:8]
                        geojson = self.get_geojson(**{'name': context["jsonfile"], 'museums': museums})
                        context["latitude"] = latitude
                        context["longitude"] = longitude

        # context["geojson_path"] = PATH_PREFIX
        context['museums'] = museums

        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):

        # EXCLUDE 11K GENERAL MUSEUMS FOR NOW -- Can always add them back later
        count_museums = Museum.objects.exclude(types__code='GMU').count()
        categories = MuseumType.objects.order_by('name').exclude(code='GMU')

        context = {
            'count_museums': count_museums,
            'categories': categories,
            'map': False,
        }

        return context

    def get_geojson(self, **kwargs):
        name = kwargs.get('name')
        museums = kwargs.get('museums')
        try:
            return GeoJSON.objects.get(name=name)
        except ObjectDoesNotExist:
            # Generate the GeoJSON, save it to a file
            if museums:
                geojson = self.generate_geojson(**{'museums': museums})
                self.save_geojson(**{'geojson': geojson, 'name': name})
                new_geojson = GeoJSON(**{
                    'name': name,
                    'url': "{0}.json".format(name),
                    })
                new_geojson.save()

    def generate_geojson(self, **kwargs):
        museums = kwargs.get('museums')
        museums_json = []
        for museum in museums:
            museums_json.append({
                "type": "Feature",
                "geometry": {
                  "type": "Point",
                  "coordinates": [
                 museum.longitude,
                 museum.latitude
                    ]
                },
                "properties": {
                  "": "<h4>{0}</h4>".format(museum.name),
                  "marker-symbol": "museum",
                  }
                })
            if museum.url:
                museums_json[-1]["properties"][""] += '<b>Website:</b> <a href="{0}" target="_blank">{0}</a><br>'.format(museum.url)

            if museum.phone:
                museums_json[-1]["properties"][""] += '<b>Phone:</b> <a href="tel:{0}" target="_blank">{0}</a><br>'.format(museum.phone)

            if museum.address:
                museums_json[-1]["properties"][""] += '{0} {1} {2} {3}'.format(museum.address, museum.city, museum.state, museum.zipcode)

            # This doesn't play nicely with Geojson.io or Google maps
            # if museum.types.code == 'ART':
            #     museums_json[-1]["properties"]["marker-color"] = "#BF0000"
            # elif museum.types.code == 'BOT':
            #     museums_json[-1]["properties"]["marker-color"] = "#CC430A"
            # elif museum.types.code == 'CMU':
            #     museums_json[-1]["properties"]["marker-color"] = "#CABA00"
            # elif museum.types.code == 'GMU':
            #     museums_json[-1]["properties"]["marker-color"] = "#007321"
            # elif museum.types.code == 'HSC':
            #     museums_json[-1]["properties"]["marker-color"] = "#0093BF"
            # elif museum.types.code == 'HST':
            #     museums_json[-1]["properties"]["marker-color"] = "#0058D8"
            # elif museum.types.code == 'NAT':
            #     museums_json[-1]["properties"]["marker-color"] = "#14008C"
            # elif museum.types.code == 'SCI':
            #     museums_json[-1]["properties"]["marker-color"] = "#45008C"
            # elif museum.types.code == 'ZAW':
            #     museums_json[-1]["properties"]["marker-color"] = "#B400BF"

        return json.dumps({
            "type": "FeatureCollection",
            "features": museums_json,
        }, indent=4, sort_keys=True)

    def save_geojson(self, **kwargs):
        geojson = kwargs.get('geojson')
        name = kwargs.get('name')
        with open("{0}{1}.json".format(PATH_PREFIX, name), 'w') as json_file:
            json_file.write(geojson)

    def get_within_radius(self, **kwargs):
        pass