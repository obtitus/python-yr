#!/usr/bin/env python3
import datetime
import json
from yr.libyr import Yr

weather = Yr(location_name='Norway/Rogaland/Stavanger/Stavanger')

hour = datetime.timedelta(hours=1)
for forecast_json in weather.forecast(as_json=True):
    # FIXME: not very user-friendly, add this filtering to the yr library?
    forecast = json.loads(forecast_json)
    time_from = datetime.datetime.strptime(forecast['@from'], '%Y-%m-%dT%H:%M:%SZ')
    time_to   = datetime.datetime.strptime(forecast['@to'], '%Y-%m-%dT%H:%M:%SZ')
    delta = time_to - time_from
    
    if delta == hour: # hour_by_hour only
        print(forecast_json)

