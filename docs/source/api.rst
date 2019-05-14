API
=========

Endpoints
---------
 * "programs": "http://activity.Hikaya.io/api/programs/",
 * "sector": "http://activity.Hikaya.io/api/sector/",
 * "projecttype": "http://activity.Hikaya.io/api/projecttype/",
 * "office": "http://activity.Hikaya.io/api/office/",
 * "siteprofile": "http://activity.Hikaya.io/api/siteprofile/",
 * "country": "http://activity.Hikaya.io/api/country/",
 * "initiations": "http://activity.Hikaya.io/api/projectagreements/",
 * "tracking": "http://activity.Hikaya.io/api/tracking/",
 * "indicator": "http://activity.Hikaya.io/api/indicator/",
 * "reportingfrequency": "http://activity.Hikaya.io/api/reportingfrequency/",
 * "tolauser": "http://activity.Hikaya.io/api/tolauser/",
 * "indicatortype": "http://activity.Hikaya.io/api/indicatortype/",
 * "objective": "http://activity.Hikaya.io/api/objective/",
 * "disaggregationtype": "http://activity.Hikaya.io/api/disaggregationtype/",
 * "level": "http://activity.Hikaya.io/api/level/",
 * "externalservice": "http://activity.Hikaya.io/api/externalservice/",
 * "externalservicerecord": "http://activity.Hikaya.io/api/externalservicerecord/",
 * "strategicobjective": "http://activity.Hikaya.io/api/strategicobjective/",
 * "stakeholder": "http://activity.Hikaya.io/api/stakeholder/",
 * "stakeholdertype": "http://activity.Hikaya.io/api/stakeholdertype/",
 * "capacity": "http://activity.Hikaya.io/api/capacity/",
 * "evaluate": "http://activity.Hikaya.io/api/evaluate/",
 * "profiletype": "http://activity.Hikaya.io/api/profiletype/",
 * "province": "http://activity.Hikaya.io/api/province/",
 * "district": "http://activity.Hikaya.io/api/district/",
 * "adminlevelthree": "http://activity.Hikaya.io/api/adminlevelthree/",
 * "village": "http://activity.Hikaya.io/api/village/",
 * "contact": "http://activity.Hikaya.io/api/contact/",
 * "documentation": "http://activity.Hikaya.io/api/documentation/",
 * "collecteddata": "http://activity.Hikaya.io/api/collecteddata/",
 * "activitytable": "http://activity.Hikaya.io/api/activitytable/",
 * "disaggregationvalue": "http://activity.Hikaya.io/api/disaggregationvalue/",
 * "projectagreements": "http://activity.Hikaya.io/api/projectagreements/",
 * "loggedusers": "http://activity.Hikaya.io/api/loggedusers/",
 * "checklist": "http://activity.Hikaya.io/api/checklist/",
 * "organization": "http://activity.Hikaya.io/api/organization/",



Example
-------
::
    curl -H "Authorization: Token adkai39a9sdfj239m0afi2" https://activity.Hikaya.io/api/programs/{{id}}/`


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
        "url": "http://activity.Hikaya.io/api/programs/1/",
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
            "http://activity.Hikaya.io/api/sector/31/",
            "http://activity.Hikaya.io/api/sector/32/"
        ],
        "country": [
            "http://activity.Hikaya.io/api/country/1/"
        ],
        "user_access": []
      },
      ...
    ]

