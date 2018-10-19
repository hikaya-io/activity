Indicator
****

Endpoint
---------
 * “indicator”: “http://activity.toladata.io/api/indicator/”,


This endpoint provides access to submitted indicators in JSON format.



GET JSON List of all Indicators
--------------------------------

Lists the programs endpoints accessible to requesting user

.. raw:: html

  <pre class="prettyprint">
  <b>GET</b> /api/indicator/
  </pre>

Example
^^^^^^^^
::

    curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/indicator/


Response
^^^^^^^^^
::

    [
      {
        "url": "http://activity.toladata.io/api/indicator/20/",
        "name": "Number and percent of households using a financial product or service developed through SimulaKO",
        "number": "3.3",
        "source": "DFID",
        "definition": "Banko accounts opened through TabanKO that enrolled in a new financial product developed by SimulaKO and opened by Banko. This does not include HH accessing their accounts through the agent network",
        "baseline": "0",
        "lop_target": "7500",
        "means_of_verification": "Banko records",
        "data_collection_method": "reviewing banko reports and data",
        "responsible_person": "Simulako research manager",
        "method_of_analysis": "",
        "information_use": "",
        "comments": "",
        "key_performance_indicator": false,
        "create_date": "2017-02-22T18:26:12Z",
        "edit_date": "2017-02-22T18:26:12Z",
        "notes": null,
        "reporting_frequency": null,
        "sector": "http://activity.toladata.io/api/sector/4/",
        "approved_by": null,
        "approval_submitted_by": null,
        "external_service_record": null,
        "indicator_type": [
            "http://activity.toladata.io/api/indicatortype/1/"
        ],
        "level": [
            "http://activity.toladata.io/api/level/3/"
        ],
        "objectives": [],
        "strategic_objectives": [],
        "disaggregation": [],
        "program": [
            "http://activity.toladata.io/api/programs/1/"
        ]
      },
      ...
    ]

GET JSON List of indicator end points using limit operators
-------------------------------------------------------

Lists the programs endpoints accesible to the requesting user based on 'start'
and/or 'limit' query parameters. Use the start parameter to skip a number
of records and the limit parameter to limit the number of records returned.

.. raw:: html

    <pre class="prettyprint">
    <b>GET</b> /api/indicator/</code>?<code>start</code>=<code>start_value</code>
    </pre>

::
    curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/indicator/?start=5
    

.. raw:: html

  <pre class="prettyprint">
  <b>GET</b> /api/indicator/</code><code>limit</code>=<code>limit_value</code>
  </pre>

::

	curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/indicator/?limit=2

.. raw:: html

  <pre class="prettyprint">
  <b>GET</b> /api/indicator/<code>{pk}</code>?<code>start</code>=<code>start_value</code>&</code><code>limit</code>=<code>limit_value</code>
  </pre>

::

	 curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/indicator/?start=3&limit=4



GET JSON List of indicator end points filter by  program name
--------------------------------------------------------------

Lists the data endpoints accessible to requesting user, for the specified
``program name`` as a query parameter.

.. raw:: html


  <pre class="prettyprint">
  <b>GET</b> /api/indicator/?<code>program_name</code>=<code>program_name</code>
  </pre>

Example
^^^^^^^^^
::

       curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/indicator/?program_name=Financial Assistance to Affected Communities


GET JSON List of indicator end points filter by program country
--------------------------------------------------------------

Lists the indicator endpoints accessible to requesting user, for the specified
``program country`` as a query parameter.

.. raw:: html


  <pre class="prettyprint">
  <b>GET</b> /api/indicator/?<code>program_country_country</code>=<code>programs_country</code>
  </pre>

Example
^^^^^^^^^
::

       curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/indicator/?program_country_country=Afghanistan


Retrieve a specific Indicator
------------------------------
Provides a list of json submitted data for a specific indicator.

.. raw:: html

  <pre class="prettyprint">
  <b>GET</b> /api/indicator/<code>{id}</code></pre>

Example
^^^^^^^^^
::

      curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/indicator/2

Response
^^^^^^^^^
::
  {
    "url": "http://activity.toladata.io/api/indicator/2/",
    "name": "Total number of male and female individuals participating in cash transfer programming (CTP)",
    "number": "1.1",
    "source": "Mercy Corps",
    "definition": "This is the total number of individuals included in the program, specifically per activity. For instance, total # of program participants receiving cash transfers, participating in CFW, receiving vouchers, or other activities falling under Early Economic Recovery (EER).",
    "baseline": "0",
    "lop_target": "1300",
    "means_of_verification": "",
    "data_collection_method": "",
    "responsible_person": "",
    "method_of_analysis": "",
    "information_use": "",
    "comments": "",
    "key_performance_indicator": true,
    "create_date": "2017-02-22T18:26:13Z",
    "edit_date": "2017-03-09T04:46:39Z",
    "notes": "",
    "reporting_frequency": null,
    "sector": "http://activity.toladata.io/api/sector/4/",
    "approved_by": null,
    "approval_submitted_by": null,
    "external_service_record": null,
    "indicator_type": [
        "http://activity.toladata.io/api/indicatortype/8/"
    ],
    "level": [
        "http://activity.toladata.io/api/level/1/"
    ],
    "objectives": [],
    "strategic_objectives": [
        "http://activity.toladata.io/api/strategicobjective/1/"
    ],
    "disaggregation": [],
    "program": [
        "http://activity.toladata.io/api/programs/1/"
    ]
  }

Paginate data of a specific form
-------------------------------------------
Returns a list of json submitted data for a specific form using page number and the number of items per page. Use the ``page`` parameter to specify page number and ``page_size`` parameter is used to set the custom page size.

Example
^^^^^^^^
::

      curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/indicator/20.json?page=1&page_size=4

