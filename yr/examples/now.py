#!/usr/bin/env python3

from yr.libyr import Yr

weather = Yr(location_name='Norge/Telemark/Skien/Skien', language_name='nb')
now = weather.now()

print(now)
