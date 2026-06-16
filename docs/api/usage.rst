.. _api_usage:

=========
API Usage
=========

In this section, we'll show how to get started with your first object type, and create an object
for this object type.

Objecttypes
===========
Before continuing, make sure you have an API token.
:ref:`admin_authentication` document describes how to do it in details.
In the examples below we use the API token with the value ``1234``.

Let's start with creating an object type. For example, you want to store data
about trees (Bomen) in your town. First, you need to decide which attributes your data
will have and to design JSON schema for trees. You can take a look at provided
:ref:`examples_index`. Here is a JSON schema which we will use in the example:

.. code-block:: json

    {
      "$schema": "https://json-schema.org/draft/2020-12/schema#",
      "$id": "https://api.vng.nl/objecttypes/boom/schema.json",
      "type": "object",
      "title": "Boom",
      "description": "Een houtachtig gewas (loofboom of conifeer) met een wortelgestel en een enkele, stevige, houtige stam, die zich boven de grond vertakt.",
      "properties": {
        "boomgroep": {
          "$id": "#/properties/boomgroep",
          "type": "string",
          "title": "Boomgroep",
          "description": "Aanduiding of de boom onderdeel is van een boomgroep.",
          "examples": [
            "Laanboom"
          ],
          "enum": [
            "Laanboom",
            "Boomweide",
            "Solitaire boom"
          ]
        },
        "boomhoogteactueel": {
          "$id": "#/properties/boomhoogteactueel",
          "type": "integer",
          "title": "BoomhoogteActueel",
          "description": "Hoogte van de boom in meters.\nEenheid: m"
        },
        "leeftijd": {
          "$id": "#/properties/leeftijd",
          "type": "integer",
          "title": "Leeftijd",
          "description": "Leeftijd van het beheerobject in jaren.\nEenheid: Aantal",
          "examples": []
        },
        "meerstammig": {
          "$id": "#/properties/meerstammig",
          "type": "boolean",
          "title": "Meerstammig",
          "description": "Aanduiding voor meerstammigheid bij een Boom"
        },
        "type": {
          "$id": "#/properties/type",
          "type": "string",
          "title": "Type",
          "description": "Typering van het beheerobject."
        }
      },
      "required": ["boomhoogteactueel", "leeftijd"]
    }


Create an object type
---------------------

Now we need to create an object type which will include this JSON schema. The object type consists
of metadata of the object type and (a version of) the JSON schema. This separation
exists because the API supports versioning of the JSON schemas. If you want to change the
JSON schema in the objecttype, a new version will be created. Therefore you don't need to worry
that a new version of the Object type schema would not match the exising objects since
these objects refer to the previous version.

So let's create the object type metadata:

.. code-block:: http

    POST /api/v2/objecttypes HTTP/1.1
    Authorization: Token 1234

    {
        "name": "boom",
        "namePlural": "bomen",
        "description": "Bomen in de publieke ruimte.",
        "dataClassification": "open",
        "maintainerOrganization": "Tree organization",
        "maintainerDepartment": "Tree API department",
        "contactPerson": "John Smith",
        "contactEmail": "john@lovestrees.nl",
        "source": "Tree navigator",
        "updateFrequency": "monthly",
        "providerOrganization": "Open data for trees",
        "documentationUrl": "http://tree-object-type.nl"
    }

The response contains the url of a freshly created object type with its unique identifier and
a list of versions of the JSON schema, which is initially empty.

.. code-block:: http

    HTTP/1.1 201 Created

    {
        "url": "http://<open-objecten-host>/api/v2/objecttypes/<object-type-uuid>",
        "name": "boom",
        "namePlural": "bomen",
        "description": "Bomen in de publieke ruimte.",
        "dataClassification": "open",
        "maintainerOrganization": "Tree organization",
        "maintainerDepartment": "Tree API department",
        "contactPerson": "John Smith",
        "contactEmail": "john@lovestrees.nl",
        "source": "Tree navigator",
        "updateFrequency": "monthly",
        "providerOrganization": "Open data for trees",
        "documentationUrl": "http://tree-object-type.nl",
        "labels": {},
        "createdAt": "2021-03-03",
        "modifiedAt": "2021-03-03",
        "versions": []
    }

Now we can add our JSON schema to the created object type as its version:

.. code-block:: http

    POST /api/v2/objecttypes/<object-type-uuid>/versions HTTP/1.1
    Authorization: Token 1234

    {
        "status": "draft",
        "jsonSchema": {
            "$schema": "https://json-schema.org/draft/2020-12/schema#",
            "$id": "https://api.vng.nl/objecttypes/boom/schema.json",
            <...>
        }
    }

The response contains the url of the created version of the object type.

.. code-block:: http

    HTTP/1.1 201 OK

    {
        "url": "http://<open-objecten-host>/api/v2/objecttypes/<object-type-uuid>/versions/1",
        "version": 1,
        "objectType": "http://<open-objecten-host>/api/v2/objecttypes/<object-type-uuid>",
        "status": "draft",
        "jsonSchema": {
            "$schema": "https://json-schema.org/draft/2020-12/schema#",
            "$id": "https://api.vng.nl/objecttypes/boom/schema.json",
            <...>
        },
        "createdAt": "2021-03-03",
        "modifiedAt": "2021-03-03",
        "publishedAt": null
    }

You can see that the ``version`` has the 'draft' status, which means, that it can be updated
without creating a new version. Once the ``version`` is set to 'published' you can't change
it anymore, unless you create a new version.

Publish an object type version
------------------------------

Let's publish our object type version. In the API you can do it with a
PATCH request:

.. code-block:: http

    PATCH /api/v2/objecttypes/<object-type-uuid>/versions/1 HTTP/1.1
    Authorization: Token 1234

    {
        "status": "published"
    }

In the response you can see that ``publishedAt`` attribute now contains the current date:

.. code-block:: http

    HTTP/1.1 200 OK

    {
        "url": "http://<open-objecten-host>/api/v2/objecttypes/<object-type-uuid>/versions/1",
        "version": 1,
        "objectType": "http://<open-objecten-host>/api/v2/objecttypes/<object-type-uuid>",
        "status": "published",
        "jsonSchema": {
            "$schema": "https://json-schema.org/draft/2020-12/schema#",
            "$id": "https://api.vng.nl/objecttypes/boom/schema.json",
            <...>
        },
        "createdAt": "2021-03-03",
        "modifiedAt": "2021-03-03",
        "publishedAt": "2021-03-03"
    }


Now, when you try to change this version a HTTP 400 error will appear indicating you cannot change it anymore.
For example:

.. code-block:: http

    PATCH /api/v2/objecttypes/<object-type-uuid>/versions/1 HTTP/1.1
    Authorization: Token 1234

    {
        "jsonSchema": {
        "$schema": "https://json-schema.org/draft/2020-12/schema#",
        "$id": "https://api.vng.nl/objecttypes/boom/schema.json",
        <...>
        "required": []
        }
    }

The response should be something like this:

.. code-block:: http

    HTTP/1.1 400 Bad Request

    {
        "non_field_errors": [
            "Only draft versions can be changed"
        ]
    }


Retrieve an object type
-----------------------

Once the object type is created it can always be retrieved by its url:

.. code-block:: http

    GET /api/v2/objecttypes/<object-type-uuid> HTTP/1.1
    Authorization: Token 1234

    HTTP/1.1 200 OK

    {
        "url": "http://<open-objecten-host>/api/v2/objecttypes/<object-type-uuid>",
        "name": "boom",
        "namePlural": "bomen",
        "description": "Bomen in de publieke ruimte.",
        "dataClassification": "open",
        "maintainerOrganization": "Tree organization",
        "maintainerDepartment": "Tree API department",
        "contactPerson": "John Smith",
        "contactEmail": "john@lovestrees.nl",
        "source": "Tree navigator",
        "updateFrequency": "monthly",
        "providerOrganization": "Open data for trees",
        "documentationUrl": "http://tree-object-type.nl",
        "labels": {},
        "createdAt": "2021-03-03",
        "modifiedAt": "2021-03-03",
        "versions": [
            "http://<open-objecten-host>/api/v2/objecttypes/<object-type-uuid>/versions/1"
        ]
    }

You can see that ``versions`` attribute includes a list of urls to all the versions of this
object type.


Objects
=======

Now we have an object type containing a JSON schema for tree objects and we are ready to
create objects. Before going further please, make sure that you configured the proper
authentication and authorizations in the admin:

* The API token has write permissions for the object type "Boom".

:ref:`admin_authentication` and :ref:`admin_authorization` document how to do it in details.

In the examples below we use the API token with the value ``5678``.

Create an object
----------------

First, let's construct some tree data that matches our JSON schema in the object type "Boom":

.. code-block:: json

    {
        "boomgroep": "Solitaire boom",
        "boomhoogteactueel": 3,
        "leeftijd": 100,
        "meerstammig": false
    }

If you want, you can validate your JSON data against the JSON schema on `JSONschema.dev <https://jsonschema.dev>`_

Using the URL of the created object type, we can create a tree object. If we have
geographic coordinates for our object we can also include them into the request
body. Don't forget the required "Content-Crs" header to indicate the coordinate
system you are using.

.. code-block:: http

    POST /api/v2/objects HTTP/1.1
    Authorization: Token 5678
    Content-Crs: EPSG:4326

    {
        "type": "http://<open-objecten-host>/api/v2/objecttypes/<object-type-uuid>",
        "record": {
            "typeVersion": 1,
            "startAt": "2021-01-01",
            "data": {
                "boomgroep": "Solitaire boom",
                "boomhoogteactueel": 3,
                "leeftijd": 100,
                "meerstammig": false
            },
            "geometry": {
                "type": "Point",
                "coordinates": [4.908722727852763, 52.36991749536178]
            }
        }
    }

The object type version is defined in ``typeVersion`` attribute. This means that we can create
objects that match any version of the particular object type but in this case we only have our
initial version. The response contains the URL of the object:

.. code-block:: http

    HTTP/1.1 201 Created

    {
        "url": "http://<open-objecten-host>/api/v2/objects/<object-uuid>",
        "type": "http://<open-objecten-host>/api/v2/objecttypes/<object-type-uuid>",
        "record": {
            "index": 1,
            "typeVersion": 1,
            "data": {
                "leeftijd": 100,
                "boomgroep": "Solitaire boom",
                "meerstammig": false,
                "boomhoogteactueel": 3
            },
            "geometry": {
                "type": "Point",
                "coordinates": [
                    4.908722727852763,
                    52.36991749536178
                ]
            },
            "startAt": "2021-01-01",
            "endAt": null,
            "registrationAt": "2021-03-03",
            "correctionFor": null,
            "correctedBy": null
        }
    }

When an object is created or updated, its data is always validated against the
JSON schema in the related object type. If the data doesn't match, the response will
contain a HTTP 400 error.

For example, let's try to create the following object:

.. code-block:: http

    POST /api/v2/objects HTTP/1.1
    Authorization: Token 5678
    Content-Crs: EPSG:4326

    {
        "type": "http://<open-objecten-host>/api/v2/objecttypes/<object-type-uuid>",
        "record": {
            "typeVersion": 1,
            "startAt": "2021-03-03",
            "data": {
                "boomgroep": "Solitaire boom",
                "boomhoogteactueel": 2.5,
                "leeftijd": 100,
            }
        }
    }

In the JSON schema ``boomhoogteactueel`` is of type integer but we provide a floating point number.
The response will look like similar to this:

.. code-block:: http

    HTTP/1.1 400 Bad Request

    {
        "non_field_errors": [
            "2.5 is not of type 'integer'"
        ]
    }


Retrieve an object
------------------

Once the object is created, it can always be retrieved by its URL:

.. code-block:: http

    GET /api/v2/objects/<object-uuid> HTTP/1.1
    Authorization: Token 5678

    HTTP/1.1 200 OK

    {
        "url": "http://<open-objecten-host>/api/v2/objects/<object-uuid>",
        "type": "http://<open-objecten-host>/api/v2/objecttypes/<object-type-uuid>",
        "record": {
            "index": 1,
            "typeVersion": 1,
            "data": {
                "leeftijd": 100,
                "boomgroep": "Solitaire boom",
                "meerstammig": false,
                "boomhoogteactueel": 3
            },
            "geometry": {
                "type": "Point",
                "coordinates": [
                    4.908722727852763,
                    52.36991749536178
                ]
            },
            "startAt": "2021-01-01",
            "endAt": null,
            "registrationAt": "2021-03-03",
            "correctionFor": null,
            "correctedBy": null
        }
    }

Retrieve objects of certain object type
---------------------------------------

The API supports different filter and search options.
You can filter objects by:

* object type
* data attributes (display all trees higher than 2 meters)
* geographic coordinates or areas (display all trees in one neighbourhood)

To filter the list by a particular object type you can use the ``type`` query parameter:

.. code-block:: http

    GET /api/v2/objects?type=http://<open-objecten-host>/api/v2/objecttypes/<object-type-uuid> HTTP/1.1
    Authorization: Token 5678

    HTTP/1.1 200 OK

    [
        {
            "url": "http://<open-objecten-host>/api/v2/objects/<object-uuid>",
            "type": "http://<open-objecten-host>/api/v2/objecttypes/<object-type-uuid>",
            "record": {
                "index": 1,
                "typeVersion": 1,
                "data": {
                    "leeftijd": 100,
                    "boomgroep": "Solitaire boom",
                    "meerstammig": false,
                    "boomhoogteactueel": 3
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        4.908722727852763,
                        52.36991749536178
                    ]
                },
                "startAt": "2021-01-01",
                "endAt": null,
                "registrationAt": "2021-03-03",
                "correctionFor": null,
                "correctedBy": null
            }
        }
    ]

Retrieve the history of an object
---------------------------------
The API supports versioning, i.e. when an object is updated, its previous states
can also be retrieved. In the API these are called ``records``.

.. code-block:: http

    GET /api/v2/objects/<object-uuid>/history HTTP/1.1
    Authorization: Token 5678

    HTTP/1.1 200 OK

    [
        {
            "index": 1,
            "typeVersion": 1,
            "data": {
                "leeftijd": 100,
                "boomgroep": "Solitaire boom",
                "meerstammig": false,
                "boomhoogteactueel": 3
            },
            "geometry": {
                "type": "Point",
                "coordinates": [
                    4.908722727852763,
                    52.36991749536178
                ]
            },
            "startAt": "2021-01-01",
            "endAt": null,
            "registrationAt": "2021-03-03",
            "correctionFor": null,
            "correctedBy": null
        }
    ]

For now we have only one record, but every time the object is changed the new record will
be created.

Retrieve an object (record) for a particular date
-------------------------------------------------

Since there could be a difference between the real date of
the object change and its registration in the system, the API support both
material and formal history. The material history describes the history as it should
be (stored in the ``startAt`` and ``endAt`` attributes). The formal history describes the
history as it was administratively processed (stored in the ``registeredAt``
attribute).

The query parameters ``date`` (material history) and ``registrationDate`` (formal history)
allow for querying the records as seen from both perspectives, and can yield different results.

For example, if you want to display all the objects as they were on 2021-02-02, you can do this from 2 perspectives.
First, let's do it from the material history perspective:

.. code-block:: http

    GET /api/v2/objects?date=2021-02-02 HTTP/1.1
    Authorization: Token 5678

    HTTP/1.1 200 OK

    [
        {
            "url": "http://<open-objecten-host>/api/v2/objects/<object-uuid>",
            "type": "http://<open-objecten-host>/api/v2/objecttypes/<object-type-uuid>",
            "record": {
                "index": 1,
                "typeVersion": 1,
                "data": {
                    "leeftijd": 100,
                    "boomgroep": "Solitaire boom",
                    "meerstammig": false,
                    "boomhoogteactueel": 3
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        4.908722727852763,
                        52.36991749536178
                    ]
                },
                "startAt": "2021-01-01",
                "endAt": null,
                "registrationAt": "2021-03-03",
                "correctionFor": null,
                "correctedBy": null
            }
        }
    ]

We received our tree object in the response, because in reality it came into existence on 2021-01-01
(``startAt``) and never ceased (``endAt`` is empty).

Now let's do the same but from a formal history perspective:

.. code-block:: http

    GET /api/v2/objects?registrationDate=2021-02-02 HTTP/1.1
    Authorization: Token 5678

    HTTP/1.1 200 OK

    []

Our tree object was created at 2021-03-03 (``registrationAt``), so it didn't exist
(administratively speaking) at 2021-02-02 yet. Hence, the response is an empty list.
