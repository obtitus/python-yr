#!/usr/bin/env python3
import datetime
from yr.libyr import Yr

weather = Yr(location_name='Norway/Rogaland/Stavanger/Stavanger')

hour = datetime.timedelta(hours=1)
for forecast in weather.forecast():
    # ('@from', '2022-01-05T18:00:00Z'), ('@to', '2022-01-05T18:00:00Z')
    time_from = datetime.datetime.strptime(forecast['@from'], '%Y-%m-%dT%H:%M:%SZ')
    time_to   = datetime.datetime.strptime(forecast['@to'], '%Y-%m-%dT%H:%M:%SZ')
    delta = time_to - time_from
    
    if delta == hour: # hour_by_hour only
        print(forecast)
