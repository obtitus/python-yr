#!/usr/bin/env python3

import logging
import os.path
import json  # Language
import tempfile  # Cache
import datetime  # Cache
import urllib.request  # Connect
import urllib.parse  # Location
import xmltodict
from xml.parsers.expat import ExpatError

log = logging.getLogger(__name__)

try:
    import yr.location_to_coordinates as location_to_coordinates
except ImportError:
    # allow calling without install
    import location_to_coordinates
    

class YrObject:

    script_directory = os.path.dirname(os.path.abspath(__file__))  # directory of the script
    encoding = 'utf-8'


class YrException(Exception):

    def __init__(self, message):
        log.error(message)
        raise


class Language(YrObject):

    directory = 'languages'
    default_language_name = 'en'
    extension = 'json'

    def __init__(self, language_name=default_language_name):
        self.language_name = language_name
        self.filename = os.path.join(
            self.script_directory,
            self.directory,
            '{language_name}.{extension}'.format(
                language_name=self.language_name,
                extension=self.extension,
            ),  # basename of filename
        )
        self.dictionary = self.get_dictionary()

    def get_dictionary(self):
        try:
            log.info('read language dictionary: {}'.format(self.filename))
            with open(self.filename, mode='r', encoding=self.encoding) as f:
                return json.load(f)
        except Exception as e:
            raise YrException(e)



class API_Locationforecast(YrObject):

    """Class to use the API of api.met.no"""

    base_url = 'https://api.met.no/weatherapi/locationforecast/2.0/classic?'
    forecast_link = 'locationforecast'

    def __init__(self, lat, lon, msl=0, language=False):
        """
        :param double lat: latitude coordinate
        :param double lon: longitude coordinate
        :param language: a Language object
        """
        self.coordinates = dict(lat=lat, lon=lon)
        self.location_name = 'lat={lat};lon={lon}'.format(**self.coordinates)
        # self.language = language if isinstance(language, Language) else Language()
        self.url = self.get_url()
        self.hash = self.get_hash()

    def get_url(self):
        """Return the url of API service"""
        return '{base_url}{location_name}'.format(
            base_url=self.base_url,
            location_name=self.location_name,
        )

    def get_hash(self):
        """Create an hash with the three coordinates"""
        return '{location_name}.{forecast_link}'.format(
            location_name=self.location_name,
            forecast_link=self.forecast_link,
        )

class Location(API_Locationforecast):
    """
    Used to call the legacy xml files which will be discontinued Feburary 2022,
    more info: https://developer.yr.no/doc/guides/getting-started-from-forecast-xml/

    Now translates into the "classic" API calls to https://api.met.no/weatherapi/locationforecast/2.0/.
    New code should instead rely on API_Locationforecast directly
    """
    default_forecast_link = 'forecast'
    forecast_links = [default_forecast_link, 'forecast_hour_by_hour']

    extension = 'xml'

    def __init__(self, location_name, forecast_link=default_forecast_link, language=False):
        self.location_name = location_name
        self.language = language if isinstance(language, Language) else Language()

        if forecast_link in self.forecast_links:  # must be valid forecast_link
            self.forecast_link = self.language.dictionary[forecast_link]
        else:
            self.forecast_link = self.default_forecast_link

        directory = tempfile.gettempdir()
        
        zip_url   = self.language.dictionary['location_zip_url']
        zip_cache = os.path.join(directory, zip_url.split('/')[-1])
        
        location = location_to_coordinates.parse_zip_cached(zip_url, zip_cache,
                                                            location_name=location_name)
        
        super().__init__(lat=location['lat'], lon=location['lon'], msl=location['altitude'])


class LocationXYZ(API_Locationforecast):  # ~> Deprecated!!!

    """Class to use the API of yr.no"""

    def __init__(self, x, y, z=0, language=False):
        """
        :param double x: longitude coordinate
        :param double y: latitude coordinate
        :param double z: altitude (meters above sea leve)
        :param language: a Language object
        """
        super().__init__(y, x, language)


class Connect(YrObject):

    def __init__(self, location):
        self.location = location

    def read(self):
        try:
            log.info('weatherdata request: {}, forecast-link: {}'.format(
                self.location.location_name,
                self.location.forecast_link,
            ))
            cache = Cache(self.location)
            if not cache.exists() or not cache.is_fresh():
                log.info('read online: {}'.format(self.location.url))
                agent = {"User-Agent" : "Python yr.no client"}
                request = urllib.request.Request(self.location.url, headers=agent)
                response = urllib.request.urlopen(request)
                if response.status != 200:
                    raise
                weatherdata = response.read().decode(self.encoding)
                cache.dump(weatherdata)
            else:
                weatherdata = cache.load()
            return weatherdata
        except Exception as e:
            raise YrException(e)


class Cache(YrObject):

    directory = tempfile.gettempdir()
    extension = 'xml'
    timeout = 15  # cache timeout in minutes

    def __init__(self, location):
        self.location = location
        self.filename = os.path.join(
            self.directory,
            '{location_hash}.{extension}'.format(
                location_hash=self.location.hash,
                extension=self.extension,
            ),  # basename of filename
        )

    def dump(self, data):
        log.info('writing cachefile: {}'.format(self.filename))
        with open(self.filename, mode='w', encoding=self.encoding) as f:
            f.write(data)

    def valid_until_timestamp_from_file(self):
        xmldata = self.load()
        d = None
        try:
            d = xmltodict.parse(xmldata)
        except ExpatError:
            return datetime.datetime.fromtimestamp(0)
        meta = d['weatherdata']['meta']
        if isinstance(self.location, API_Locationforecast):
            if isinstance(meta['model'], dict):
                next_update = meta['model']['@nextrun']
            elif isinstance(meta['model'], list):
                next_update = meta['model'][0]['@nextrun']
            else:
                return False
            next_update = next_update.replace("Z", " +0000")
            date_format = "%Y-%m-%dT%H:%M:%S %z"
            # Read the UTC timestamp, convert to local time and remove the timezone information.
            valid_until = datetime.datetime.strptime(next_update,date_format)
            valid_until = valid_until.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None).replace(tzinfo=None)
        else:
            next_update = meta['nextupdate']
            date_format = '%Y-%m-%dT%H:%M:%S'
            valid_until = datetime.datetime.strptime(next_update, date_format)
        # hotfix API_Locationforecast ++ @nextrun <<<
        log.info('Cache is valid until {}'.format(valid_until))
        return valid_until

    def is_fresh(self):
        log.info('Now is {}'.format(datetime.datetime.now()))
        return datetime.datetime.now() <= self.valid_until_timestamp_from_file()

    def exists(self):
        return os.path.isfile(self.filename)

    def load(self):
        log.info('read from cachefile: {}'.format(self.filename))
        with open(self.filename, mode='r', encoding=self.encoding) as f:
            return f.read()

    def remove(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)
            log.info('removed cachefile: {}'.format(self.filename))

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    log.info('starting __main__')

    weatherdata = Connect(Location(
        location_name='Czech_Republic/Prague/Prague',
        forecast_link='forecast',
        language=Language(language_name='en'),
    )).read()
    #print(weatherdata)

    weatherdata = Connect(Location(
        location_name='Czech_Republic/Prague/Prague',
        forecast_link='forecast_hour_by_hour',
        language=Language(language_name='en'),
    )).read()
    # print(weatherdata)

    weatherdata = Connect(API_Locationforecast(
        50.0596696,
        14.4656239,
        11,
        language=Language(language_name='en'),
    )).read()
    # print(weatherdata)

    logging.info('stopping __main__')
