#!/usr/bin/env python3

from yr.libyr import Yr

weather = Yr(location_name='Norge/Telemark/Skien/Skien', language_name='nb')

data = list()
for forecast in weather.forecast():
    if 'windSpeed' in forecast:
        row = {'from': forecast['@from'], 'to': forecast['@to'], 'speed': float(forecast['windSpeed']['@mps'])}
        data.append(row)

wind_speed = dict()
wind_speed['data'] = data
wind_speed['credit'] = weather.credit        


print(wind_speed)
