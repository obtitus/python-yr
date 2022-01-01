#!/usr/bin/env python3
import os
import io
import re
import csv
import time
import shelve
import functools
import zipfile
import tempfile  # Cache
import urllib.request
import logging
log = logging.getLogger(__name__)

directory = tempfile.gettempdir()
shelve_filename = os.path.join(directory, 'yr_location_to_coordinates.shelve')

class APIError(Exception):
    pass

'''
Changes to API no longer allow a location string (i.e. Czech_Republic/Prague/Prague), only lat/lon, see
https://developer.yr.no/doc/guides/getting-started-from-forecast-xml/
This file aids this transition by using the provided .zip files on the above page.
NOTE: This is very slow (downloading zip, unzipping, searching csv files) hence updating code to use coordinates instead is recommended.
'''

def file_age(filename):
    '''
    Returns age of the file in days
    '''
    fileChanged = os.path.getmtime(filename)
    now = time.time()
    age = (now - fileChanged)/(60*60*24) # age of file in days
    log.debug('file_age(%s) -> %.1f days', filename, age)
    return age

def get_zip_cached(url, cache_filename, old_age_days=30): # assume the zip files (never?) changes
    '''
    Downloads binary filename given by url unless cache_filename is newer than old_age_days.

    Returns: cache_filename

    May raise APIError if the status code is not 200.
    '''
    if os.path.exists(cache_filename):
        age = file_age(cache_filename)
        if age < old_age_days:
            log.info('returning cached %s, age = %d days', cache_filename, age)
            return cache_filename
    # else

    # FIXME: merge with Connect() class?
    agent = {"User-Agent" : "Python yr.no client"}
    request = urllib.request.Request(url, headers=agent)
    log.info('Getting %s', url)
    response = urllib.request.urlopen(request)
    if response.status != 200:
        raise APIError("Invalid responce from %s, expected status 200, got %s" % (url, response.status))

    try:
        with open(cache_filename, 'wb') as f:
            f.write(response.read())
    except Exception as e:
        log.error('Zip download failed, clearing cache')
        try:
            os.remove(cache_filename)
        except:
            pass

    return cache_filename

def parse_location_csv(f, location_name):
    '''
    Parses the location csv file from 
    https://www.yr.no/storage/lookup/Norsk.csv.zip or 
    https://www.yr.no/storage/lookup/English.csv.zip
    where location_name is expected to be found in column 0 and the returned value is in column 1. See
    https://developer.yr.no/doc/guides/getting-started-from-forecast-xml/
    '''
    encoder = io.TextIOWrapper(f)
    csvreader = csv.reader(encoder, delimiter='\t')
    lat_lon_str = None
    for row in csvreader:
        if row[0] == location_name:
            lat_lon_str = row[1] 
            break # returns first match
    else: # for loop failed
        return None

    pattern = 'lat=([\d.]+)&lon=([\d.]+)&altitude=([\d.]+)'
    reg = re.match(pattern, lat_lon_str)
    result = None
    if reg:
        result = dict()
        result['lat'] = float(reg.group(1))
        result['lon'] = float(reg.group(2))
        result['altitude'] = float(reg.group(3))
    else:
        raise APIError('Expected lat/lon/altitude string matching %s, got %s' % (pattern, lat_lon_str))

    return result

def shelve_cache(func):
    '''
    Wrapper for persistent storage of return value using python shelves module.
    Note: never expires, grows forever. 
    Assumption is that the user probably only wants weather for a 
    few different location names and that the yr database never updates the lat/lon for a given location.
    '''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        cache_key = repr(args) + repr(kwargs) # yes, this will change if the parameter order changes, but who cares.

        # is it cached?
        with shelve.open(shelve_filename) as f:
            if cache_key in f:
                log.debug('Returning shelve cache %s from %s', cache_key, shelve_filename)
                return f[cache_key]
        
        # guess not, call function
        ret = func(*args, **kwargs)

        # save for next time
        with shelve.open(shelve_filename) as f:
            f[cache_key] = ret

        return ret

    return wrapper
        
@shelve_cache
def parse_zip_cached(url, cache_filename, location_name):
    '''
    Main function to call, takes
    :param string url: either https://www.yr.no/storage/lookup/Norsk.csv.zip or https://www.yr.no/storage/lookup/English.csv.zip
    :param string cache_filename: i.e. /tmp/Norsk.csv.zip
    :param string location_name: location to search for, i.e. "Czech_Republic/Prague/Prague"
    :return dict: dictionary with {'lat': ..., 'lon': ..., 'altitude': ...}

    Effort is made to only download the rather large zip file once and to also cache the search to disk, so that subsequent calls with the
    same location is as fast as possible.

    :raises APIError: if the url is invalid/fails to download
    :raises APIError: if the location is not found
    '''
    zip_filename = get_zip_cached(url, cache_filename)

    location_name = location_name.lower() # case insensitive
    location_name = location_name.replace(" ", "_") # use _ instead of space
    country = location_name.split('/')[0] # Czech_Republic/Prague/Prague -> Czech_Republic

    search_for = country + '.csv'
    results = list()
    with zipfile.ZipFile(zip_filename, 'r') as z:
        # find country csv filename(s)
        matches = list() 
        for name in z.namelist():
            if name.endswith(search_for):
               matches.append(name)

        log.info('searching %s', matches)               
        if len(matches) == 0:
            raise APIError("Unable to find %s in %s" % (search_for, zip_filename))
        
        # find correct row in csv file(s)
        for name in matches: # hopefully only 1 file, but lets allow multiple
            with z.open(name, 'r') as f:
                res = parse_location_csv(f, location_name)
                if res is not None:
                    results.append(res)

    if len(results) == 0:
        raise APIError("Unable to find %s in %s.%s" % (location_name, zip_filename, matches))
    elif len(results) > 1:
        raise APIError("Multiple matches for %s in %s.%s" % (location_name, zip_filename, matches))
    else:
        result = results[0]

    log.info('%s(%s) -> %s', url, location_name, result)
    return result
                
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    log.info('starting __main__')

    # Test download
    directory = tempfile.gettempdir()
    url_root = 'https://www.yr.no/storage/lookup/'
    url_filename = list()
    for name in ['Norsk.csv.zip',
                 'English.csv.zip']:        
        url      = url_root + name
        filename = os.path.join(directory, name)
        get_zip_cached(url, filename)
        url_filename.append((url, filename)) # ugly hack, url_filename[0] for Norsk and url_filename[1] for English

    # Test parsing
    location = 'Czech_Republic/Prague/Prague'
    res = parse_zip_cached(url_filename[1][0], url_filename[1][1], location)
    print(location, res) # {'lat': 50.08804, 'lon': 14.42076, 'altitude': 202.0}

    location = 'Norway/Rogaland/Stavanger/Stavanger'
    res = parse_zip_cached(url_filename[1][0], url_filename[1][1], location)
    print(location, res)

    location = 'Norge/Telemark/Skien/Skien'
    res = parse_zip_cached(url_filename[0][0], url_filename[0][1], location)
    print(location, res)

    location = 'Norge/Viken/Nordre Follo/Ski'
    res = parse_zip_cached(url_filename[0][0], url_filename[0][1], location)
    print(location, res)
