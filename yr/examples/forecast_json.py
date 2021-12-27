#!/usr/bin/env python3

from yr.libyr import Yr

weather = Yr(location_name='Norge/Telemark/Skien/Skien',
             language_name='nb')

for forecast in weather.forecast(as_json=True):
    print(forecast)
