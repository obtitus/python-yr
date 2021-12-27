#!/usr/bin/env python3

from yr.libyr import Yr

weather = Yr(location_name='Norway/Rogaland/Stavanger/Stavanger',
             forecast_link='forecast_hour_by_hour',
             language_name='nb')

for forecast in weather.forecast(as_json=True):
    print(forecast)
