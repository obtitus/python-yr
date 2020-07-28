Changelog
=========
1.4.7 (2020 July 28)

* Now using version 2.0 of the met.no's locationforecast

1.4.5 (2016 May 19)

* Parse the 'nextrun' field from the cache file as UTC time (API_Locationforecast)

1.4.4 (2016 May 06)

* switched API_Locationforecast to https://api.met.no - fixing #34

1.4.2 (2015 Apr 21)

* add remove function to Cache
* add explicit installation of language-specific JSON files to setup ~> thanx to kurisuke_
* check the freshness of cache based on nextupdate tag in meta ~> thanx to knightsamar_

1.4.1 (2014 Dec 11)

* add logging support
* mod some variables
* mod catching exceptions
* rewrite LocationXYZ functionality to API_Locationforecast
    * swap longitude and latitude
    * add self.coordinates
    * add self.location_name ~> not ideal, so it will probably change in future
* add LocationXYZ wrapper over API_Locationforecast for backward compatibility
* mod hash names for temporary files
* improve setup.py
* mod README from Markdown to reStructuredText

1.4.0 (2014 Sep 12)

* add support for yr.no api service ~> thanks to lucadelu_
* add hourly forecast ~> thanks to antorweep1987_

1.3.2 (2014 Jul 11)

* improve exception-handling ~> thanks to mbambas_

1.3.1.1 (2014 Jul 10)

* bugfix: pypi/pip installer in 'setup.py'

1.3.1 (2014 Jul 10)

* bugfix: caching mechanism in 'is_fresh' function ~> thanks to antorweep1987_
* improve examples

.. _antorweep1987: https://github.com/antorweep1987
.. _mbambas: https://github.com/mbambas
.. _lucadelu: https://github.com/lucadelu
.. _kurisuke: https://github.com/kurisuke
.. _knightsamar: https://github.com/knightsamar
