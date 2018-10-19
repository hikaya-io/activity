Sector
****

Endpoint
---------
 * “sector”: “http://activity.toladata.io/api/sector/”,


This endpoint provides access to submitted sectors in JSON format.



GET JSON List of all Sectors
--------------------------------

Lists the sector endpoints accessible to requesting user

.. raw:: html

  <pre class="prettyprint">
  <b>GET</b> /api/sector/
  </pre>

Example
^^^^^^^^
::

    curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/sector/


Response
^^^^^^^^^
::

    [
        {
        "url": "http://activity.toladata.io/api/sector/11/",
        "sector": "Agribusiness",
        "create_date": "2015-04-30T21:08:12Z",
        "edit_date": "2016-02-01T15:03:47Z"
        },
        ...
    ]

GET JSON List of sector end points using limit operators
-------------------------------------------------------

Lists the programs endpoints accesible to the requesting user based on 'start'
and/or 'limit' query parameters. Use the start parameter to skip a number
of records and the limit parameter to limit the number of records returned.

.. raw:: html

    <pre class="prettyprint">
    <b>GET</b> /api/sector/</code>?<code>start</code>=<code>start_value</code>
    </pre>

::
    curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/sector/?start=5
    

.. raw:: html

  <pre class="prettyprint">
  <b>GET</b> /api/sector/</code><code>limit</code>=<code>limit_value</code>
  </pre>

::

	curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/sector/?limit=2

.. raw:: html

  <pre class="prettyprint">
  <b>GET</b> /api/sector/<code>{pk}</code>?<code>start</code>=<code>start_value</code>&</code><code>limit</code>=<code>limit_value</code>
  </pre>

::

	 curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/sector/?start=3&limit=4


Retrieve a specific Sector
---------------------------
Provides a list of json submitted data for a specific sector.

.. raw:: html

  <pre class="prettyprint">
  <b>GET</b> /api/sector/<code>{id}</code></pre>

Example
^^^^^^^^^
::

      curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/sector/22

Response
^^^^^^^^^
::
  {
    "url": "http://activity.toladata.io/api/sector/22/",
    "sector": "Agriculture",
    "create_date": "2015-11-25T02:23:46Z",
    "edit_date": "2015-11-25T02:23:46Z"
  }




Paginate data of a specific form
-------------------------------------------
Returns a list of json submitted data for a specific form using page number and the number of items per page. Use the ``page`` parameter to specify page number and ``page_size`` parameter is used to set the custom page size.

Example
^^^^^^^^
::

      curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/sector.json?page=1&page_size=4

