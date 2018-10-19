API
=========

Endpoints
---------
 * "programs": "http://activity.toladata.io/api/programs/",
 * "sector": "http://activity.toladata.io/api/sector/",
 * "projecttype": "http://activity.toladata.io/api/projecttype/",
 * "office": "http://activity.toladata.io/api/office/",
 * "siteprofile": "http://activity.toladata.io/api/siteprofile/",
 * "country": "http://activity.toladata.io/api/country/",
 * "initiations": "http://activity.toladata.io/api/projectagreements/",
 * "tracking": "http://activity.toladata.io/api/tracking/",
 * "indicator": "http://activity.toladata.io/api/indicator/",
 * "reportingfrequency": "http://activity.toladata.io/api/reportingfrequency/",
 * "tolauser": "http://activity.toladata.io/api/tolauser/",
 * "indicatortype": "http://activity.toladata.io/api/indicatortype/",
 * "objective": "http://activity.toladata.io/api/objective/",
 * "disaggregationtype": "http://activity.toladata.io/api/disaggregationtype/",
 * "level": "http://activity.toladata.io/api/level/",
 * "externalservice": "http://activity.toladata.io/api/externalservice/",
 * "externalservicerecord": "http://activity.toladata.io/api/externalservicerecord/",
 * "strategicobjective": "http://activity.toladata.io/api/strategicobjective/",
 * "stakeholder": "http://activity.toladata.io/api/stakeholder/",
 * "stakeholdertype": "http://activity.toladata.io/api/stakeholdertype/",
 * "capacity": "http://activity.toladata.io/api/capacity/",
 * "evaluate": "http://activity.toladata.io/api/evaluate/",
 * "profiletype": "http://activity.toladata.io/api/profiletype/",
 * "province": "http://activity.toladata.io/api/province/",
 * "district": "http://activity.toladata.io/api/district/",
 * "adminlevelthree": "http://activity.toladata.io/api/adminlevelthree/",
 * "village": "http://activity.toladata.io/api/village/",
 * "contact": "http://activity.toladata.io/api/contact/",
 * "documentation": "http://activity.toladata.io/api/documentation/",
 * "collecteddata": "http://activity.toladata.io/api/collecteddata/",
 * "tolatable": "http://activity.toladata.io/api/tolatable/",
 * "disaggregationvalue": "http://activity.toladata.io/api/disaggregationvalue/",
 * "projectagreements": "http://activity.toladata.io/api/projectagreements/",
 * "loggedusers": "http://activity.toladata.io/api/loggedusers/",
 * "checklist": "http://activity.toladata.io/api/checklist/",
 * "organization": "http://activity.toladata.io/api/organization/",



Example
-------
::
    curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.toladata.io/api/programs/{{id}}/`


GET /api/programs/

HTTP 200 OK
Allow: GET, POST, OPTIONS
Content-Type: application/json
Vary: Accept

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

