API_VERSION = "2.5.1"
VERSIONS = {"v1": "1.3.0", "v2": "2.5.1"}

# api settings
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_FILTER_BACKENDS": ["vng_api_common.filters.Backend"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "objects.token.authentication.TokenAuthentication"
    ],
    "DEFAULT_SCHEMA_CLASS": "objects.utils.autoschema.AutoSchema",
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
    "DEFAULT_VERSION": "v2",  # NOT to be confused with API_VERSION - it's the major version part
    "ALLOWED_VERSIONS": ("v1", "v2"),
    "VERSION_PARAM": "version",
    "EXCEPTION_HANDLER": "objects.utils.views.exception_handler",
    # test
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

description = """An API to manage Objects.

# Introduction

An OBJECT is of a certain OBJECTTYPE (defined in the Objecttypes API). An
OBJECT has a few core attributes that every OBJECT (technically a RECORD,
see below) has, although these attributes can sometimes be empty. They are
attributes like `geometry` and some administrative attributes. The data that
describes the actual object is stored in the `data` attribute and follows
the JSON schema as given by the OBJECTTYPE.

## Validation

When an OBJECT is created or changed the `OBJECT.type` attribute refers to the
matching OBJECTTYPE in the Objecttypes API. The RECORD always indicates which
OBJECTTYPE-VERSION is used, shown in the `RECORD.typeVersion` attribute.

Using these 2 attributes, the appropriate JSON schema is retrieved from the
Objecttypes API and the OBJECT data is validated against this JSON schema.

## History

Each OBJECT has 1 or more RECORDs. A RECORD contains the data of an OBJECT
at a certain time. An OBJECT can have multiple RECORDS that describe the
history of that OBJECT. Changes to an OBJECT actually create a new RECORD
under the OBJECT and leaves the old RECORD as is.

### Material and formal history

History can be seen from 2 perspectives: formal and material history. The
formal history describes the history as it should be (stored in the
`startAt` and `endAt` attributes). The material history describes the
history as it was administratively processed (stored in the `registeredAt`
attribute).

The difference is that an object could be created or updated in the real
world at a certain point in time but the administrative change (ie. save or
update the object in the Objects API) can be done at a later time. The
query parameters `?date=2021-01-01` (formal history) and
`?registrationDate=2021-01-01` (material history) allow for querying the
RECORDS as seen from both perspectives, and can yield different results.

### Corrections

RECORDs cannot be deleted or changed once saved. If an error was made to
a RECORD, the RECORD can be "corrected" by saving a new RECORD and indicate
that it corrects a previous RECORD. This is done via the attribute
`correctionFor`.

### Deletion

Although OBJECTs can be deleted, it is sometimes better to set the
`endDate` of an OBJECT. Deleting an OBJECT also deletes all RECORDs in
accordance with privacy laws.

# Authorizations

The API uses API-tokens that grant certain permissions. The API-token is
passed via a header, like this: `Authorization: Token <token>`

# Notifications

When OBJECTs are created, updated or deleted via the API, notifications of
these operations are published to the configured Notifications API in the
`objecten` channel.
"""

SPECTACULAR_SETTINGS = {
    "REDOC_DIST": "SIDECAR",
    "SCHEMA_PATH_PREFIX": r"/api/v[1-9]+",
    "SCHEMA_PATH_PREFIX_TRIM": True,
    "TITLE": "Objects API",
    "DESCRIPTION": description,
    "SERVE_INCLUDE_SCHEMA": False,
    "CONTACT": {
        "url": "https://github.com/maykinmedia/objects-api",
    },
    "LICENSE": {"name": "EUPL-1.2"},
    "EXTERNAL_DOCS": {
        "url": "https://objects-and-objecttypes-api.readthedocs.io/",
    },
    "VERSION": None,
    "COMPONENT_NO_READ_ONLY_REQUIRED": True,
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.hooks.postprocess_schema_enums",
        "objects.utils.hooks.postprocess_servers",
        "objects.utils.hooks.postprocess_versions",
    ],
    "TAGS": [{"name": "objects"}, {"name": "permissions"}],
}

OAS_SERVERS = {"v1": [{"url": "/api/v1"}], "v2": [{"url": "/api/v2"}]}

UNAUTHORIZED_FIELDS_HEADER = "X-Unauthorized-Fields"
