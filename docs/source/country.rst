Country
****

Endpoint
---------
 * “country”: “http://activity.toladata.io/api/country/”,


This endpoint provides access to submitted countries in JSON format.



GET JSON List of all Countries
--------------------------------

Lists the countries endpoints accessible to requesting user

.. raw:: html

  <pre class="prettyprint">
  <b>GET</b> /api/country/
  </pre>

Example
^^^^^^^^
::

    curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/country/


Response
^^^^^^^^^
::

    [
        {
        "url": "http://activity.toladata.io/api/country/1/",
        "country": "Afghanistan",
        "code": "AF",
        "description": "",
        "latitude": "34.5333",
        "longitude": "69.1333",
        "zoom": 5,
        "create_date": "2015-02-05T21:21:53Z",
        "edit_date": "2015-04-14T17:09:07Z",
        "organization": "http://activity.toladata.io/api/organization/1/"
        },
        ...
    ]


GET JSON List of countries end points using limit operators
-------------------------------------------------------

Lists the programs endpoints accesible to the requesting user based on 'start'
and/or 'limit' query parameters. Use the start parameter to skip a number
of records and the limit parameter to limit the number of records returned.

.. raw:: html

    <pre class="prettyprint">
    <b>GET</b> /api/country/</code>?<code>start</code>=<code>start_value</code>
    </pre>

::
    curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/country/?start=5
    

.. raw:: html

  <pre class="prettyprint">
  <b>GET</b> /api/country/</code><code>limit</code>=<code>limit_value</code>
  </pre>

::

	curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/country/?limit=2

.. raw:: html

  <pre class="prettyprint">
  <b>GET</b> /api/country/<code>{pk}</code>?<code>start</code>=<code>start_value</code>&</code><code>limit</code>=<code>limit_value</code>
  </pre>

::

	 curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/country/?start=3&limit=4


Retrieve a specific Country
----------------------------
Provides a list of json submitted data for a specific country

.. raw:: html

  <pre class="prettyprint">
  <b>GET</b> /api/country/<code>{id}</code></pre>

Example
^^^^^^^^^
::

      curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/country/2

Response
^^^^^^^^^
::
  {
    "url": "http://activity.toladata.io/api/country/2/",
    "country": "Pakistan",
    "code": "PK",
    "description": "",
    "latitude": "33.6667",
    "longitude": "73.1667",
    "zoom": 5,
    "create_date": "2015-04-14T17:12:49Z",
    "edit_date": "2015-04-14T17:12:49Z",
    "organization": "http://activity.toladata.io/api/organization/1/"
  }


Paginate data of a specific form
-------------------------------------------
Returns a list of json submitted data for a specific form using page number and the number of items per page. Use the ``page`` parameter to specify page number and ``page_size`` parameter is used to set the custom page size.

Example
^^^^^^^^
::

      curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/country.json?page=1&page_size=4

