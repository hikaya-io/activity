Programs
****

Endpoint
---------
 * "programs": "http://activity.toladata.io/api/programs/",


This endpoint provides access to submitted programs in JSON format. Where:

- ``id`` - the form unique identifier




GET JSON List of all Programs
--------------------------------

Lists the programs endpoints accessible to requesting user

.. raw:: html

  <pre class="prettyprint">
  <b>GET</b> /api/programs/
  </pre>

Example
^^^^^^^^
::

    curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/programs/


Response
^^^^^^^^^
::

    [
      {
        "url": "http://activity.toladata.io/api/programs/1/",
        "gaitid": "1001",
        "name": "Financial Assistance to Affected Communities",
        "funding_status": "Funded",
        "cost_center": "12345",
        "description": "DFID Funded Cash Emergency Distribution Program",
        "create_date": "2017-02-22T18:25:37Z",
        "edit_date": "2017-06-26T15:05:39Z",
        "budget_check": true,
        "public_dashboard": true,
        "fund_code": [],
        "sector": [
            "http://activity.toladata.io/api/sector/31/",
            "http://activity.toladata.io/api/sector/32/"
        ],
        "country": [
            "http://activity.toladata.io/api/country/1/"
        ],
        "user_access": []
      },
      ...
    ]

GET JSON List of programs end points using limit operators
-------------------------------------------------------

Lists the programs endpoints accesible to the requesting user based on 'start'
and/or 'limit' query parameters. Use the start parameter to skip a number
of records and the limit parameter to limit the number of records returned.

.. raw:: html

    <pre class="prettyprint">
    <b>GET</b> /api/programs/</code>?<code>start</code>=<code>start_value</code>
    </pre>

::
    curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/programs/?start=5
    

.. raw:: html

  <pre class="prettyprint">
  <b>GET</b> /api/programs/</code><code>limit</code>=<code>limit_value</code>
  </pre>

::

	curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/programs/?limit=2

.. raw:: html

  <pre class="prettyprint">
  <b>GET</b> /api/programs/<code>{pk}</code>?<code>start</code>=<code>start_value</code>&</code><code>limit</code>=<code>limit_value</code>
  </pre>

::

	 curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/programs/?start=3&limit=4



GET JSON List of data end points filter by name
------------------------------------------------

Lists the data endpoints accessible to requesting user, for the specified
``name`` as a query parameter.

.. raw:: html


  <pre class="prettyprint">
  <b>GET</b> /api/programs/?<code>name</code>=<code>programs_name</code>
  </pre>

Example
^^^^^^^^^
::

       curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/programs/?name=Financial Assistance to Affected Communities


GET JSON List of data end points filter by country
--------------------------------------------------

Lists the programs endpoints accessible to requesting user, for the specified
``country`` as a query parameter.

.. raw:: html


  <pre class="prettyprint">
  <b>GET</b> /api/programs/?<code>country_country</code>=<code>programs_country</code>
  </pre>

Example
^^^^^^^^^
::

       curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/programs/?country_country=Afghanistan


Retrieve a specific Program
----------------------------
Provides a list of json submitted data for a specific program.

.. raw:: html

  <pre class="prettyprint">
  <b>GET</b> /api/programs/<code>{id}</code></pre>

Example
^^^^^^^^^
::

      curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/programs/1

Response
^^^^^^^^^
::
  {
    "url": "http://activity.toladata.io/api/programs/1/",
    "gaitid": "1001",
    "name": "Financial Assistance to Affected Communities",
    "funding_status": "Funded",
    "cost_center": "12345",
    "description": "DFID Funded Cash Emergency Distribution Program",
    "create_date": "2017-02-22T18:25:37Z",
    "edit_date": "2017-06-26T15:05:39Z",
    "budget_check": true,
    "public_dashboard": true,
    "fund_code": [],
    "sector": [
        "http://activity.toladata.io/api/sector/31/",
        "http://activity.toladata.io/api/sector/32/"
    ],
    "country": [
        "http://activity.toladata.io/api/country/1/"
    ],
    "user_access": []
  }




Paginate data of a specific form
-------------------------------------------
Returns a list of json submitted data for a specific form using page number and the number of items per page. Use the ``page`` parameter to specify page number and ``page_size`` parameter is used to set the custom page size.


Example
^^^^^^^^
::

      curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/programs/1.json?page=1&page_size=4


Create a new Program
^^^^^^^^^^^^^^^^^^^^^

.. raw:: html

  <pre class="prettyprint">
  <b>POST</b> /api/programs/</pre>

Example
-------
::

        {
            'name': 'My Program',
            'gaitid': '1111',
            'country':  ["http://activity.toladata.io/api/country/1/"]
        }

Response
--------

::

        {
        "url": "http://activity.toladata.io/api/programs/588/",
        "gaitid": "1111",
        "name": "My Program",
        "funding_status": "",
        "cost_center": null,
        "description": null,
        "create_date": "2017-06-27T15:29:37Z",
        "edit_date": "2017-06-27T15:29:37Z",
        "budget_check": false,
        "public_dashboard": false,
        "fund_code": [],
        "sector": [],
        "country": [
            "http://activity.toladata.io/api/country/1/"
        ],
        "user_access": []
    
    }



