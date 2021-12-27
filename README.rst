=========
python-yr
=========

Library for the norwegian weather service YR.no_ in Python_.

Install (easiest way)
=====================

.. code:: bash

    pip3 install python-yr

Usage
=====

.. code:: python

    from yr.libyr import Yr

    weather = Yr(location_name='Norge/Telemark/Skien/Skien', language_name='nb')
    now = weather.now(as_json=True)

    print(now)

This returns
============

.. code:: json

    {
        "@from": "2014-06-04T08:00:00", 
        "@to": "2014-06-04T12:00:00", 
        "@period": "1", 
        "symbol": {
            "@number": "3", 
            "@numberEx": "3", 
            "@name": "Partly cloudy", 
            "@var": "03d"
        }, 
        "precipitation": {
            "@value": "0", 
            "@minvalue": "0", 
            "@maxvalue": "0.1"
        }, 
        "windDirection": {
            "@deg": "159.4", 
            "@code": "SSE", 
            "@name": "South-southeast"
        }, 
        "windSpeed": {
            "@mps": "1.3", 
            "@name": "Light air"
        }, 
        "temperature": {
            "@unit": "celsius", 
            "@value": "13"
        }, 
        "pressure": {
            "@unit": "hPa", 
            "@value": "1012.1"
        }
    }

For more usage examples visit folder examples_ or project wiki_

Pull requests
=============

Please everyone involved to generate demands and plans (pull requests), so we could set targets for next version 1.5 ;)

Branches
========

* develop_, the main (default) branch for development on GitHub_
* master_, branch for the stable release published on PyPi_
* python2_, branch with support for Python2
* csv-support_, branch with support for CSV export forecasts
* ...

.. _YR.no: http://www.yr.no/
.. _Python: http://www.python.org/
.. _examples: https://github.com/wckd/python-yr/blob/master/yr/examples
.. _wiki: https://github.com/wckd/python-yr/wiki
.. _develop: https://github.com/wckd/python-yr/tree/develop
.. _GitHub: https://github.com/wckd/python-yr/
.. _master: https://github.com/wckd/python-yr/tree/master
.. _PyPi: https://pypi.python.org/pypi/python-yr/
.. _python2: https://github.com/wckd/python-yr/tree/python2
.. _csv-support: https://github.com/wckd/python-yr/tree/csv-support
