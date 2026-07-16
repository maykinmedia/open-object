==============
Change history
==============

2.5.1 (2026-07-16)
------------------

**Security patches**

* [CVE ID pending] See `GHSA-55w6-rqp5-j5wx`_ for more information.

  * Ensure authorizations linked to API token are properly applied to the object history detail endpoint

.. _GHSA-55w6-rqp5-j5wx: https://github.com/maykinmedia/open-object/security/advisories/GHSA-55w6-rqp5-j5wx

2.5.0 (2025-01-09)
------------------

**Breaking changes**

* upgraded ``django-setup-configuration`` to ``0.5.0``

.. warning::

    Previous configuration files used for ``setup_configuration`` do not work.
    See the `documentation <https://objects-and-objecttypes-api.readthedocs.io/en/latest/installation/config_cli.html>`_
    for the available settings that can now be configured through ``setup_configuration``.

* added support for configuring permissions through ``django-setup-configuration``
  version ``0.4.0`` [#497]
* added support for configuring token authorizations through ``django-setup-configuration``
  version ``0.4.0`` [#485]
* added support for configuring ``mozilla-django-oidc-db`` through ``django-setup-configuration``
  version ``0.4.0`` [#490]
* added support for configuring ``OBJECTTYPE``'s through ``django-setup-configuration``
  version ``0.4.0`` [#467]
* added support for configuring Notificatiescomponentconfiguratie through ``django-setup-configuration``
  version ``0.4.0`` [#484]

**New features**

* added the new ``data_attrs`` query parameter for the ``OBJECT``'s resource [#472]

.. warning::

    Usage of the `data_attr` query parameter is deprecated. Usage of the
    new `data_attrs` query parameter is recommended.

* updated OAF version to 0.9.1. This upgrade allows admin users managing their sessions through the admin.


**Bugfixes and QOL**

* fixed ``latest`` docker image tag not being pushed [open-api-framework/#92]
* fixed documentation building in CI [#501]
* included ``gettext`` in docker images [#495]
* updated zgw-consumers to 0.35.1 [open-api-framework/#66]

.. warning::

    Configuring external services is now done through the ``Service`` model. This
    replaces the ``APICredential`` model in the admin interface. A data migration
    was added to move to the `Service` model. It is advised to verify the ``Service``
    instances in the admin to check that the data migration was ran as expected.

* updated PATCH request behaviour for the ``data`` field [#466]
* fixed CSP errors [open-api-framework/#68]

**Project maintenance**

* implementend CI action to create a PR with latest OAF version [open-api-framework/#44]
* security updates [open-api-framework/#93]
* switched from ``pip-compile`` to ``uv`` [open-api-framework/#81]
* pinned ``publish`` workflow to ``v3.0.1`` [#504]
* implementend open-api-workflows [open-api-framework/#13]

** Documentation**

* added documentation for notification retry behavior [#403]
* added missing changelog entry [#455]

2.4.4 (2024-10-01)
------------------

**Bugfixes and QOL**

* fixed CSP errors on the OAS page (#458)
* fixed OIDC login by making SameSite setting lax (#458)
* fixed adding permissions in the Admin (#449)
* fixed ``NOTIFICATIONS_DISABLED`` setting (#452)

**Project maintenance**

* added CI action to check if OAF is up-to-date (#443)

2.4.3 (2024-09-18)
------------------

**New features**

* added an endpoint to retrieve a specific object version (#328)
* supported the `in` operator in `data_attrs` to match one element (#414)

**Bugfixes and QOL**

* hid previous records available on particular date even if they match search parameters (#324)
* fixed 2FA app title (#442)
* bumped setuptools and npm dependencies (#441)

**Project maintenance**

* disabled configuration steps by default (#446)
* increase default values for uwsgi processes and threads (#448)

.. warning::

    All configuration steps are now disabled by default. To enable them use the correspondent
    environment variables


2.4.2 (2024-08-26)
------------------

**New features**

* updated open-api-framework to 0.8.0, which includes adding CSRF, CSP and HSTS settings (#438).
  All new environment variables are added to the `documentation <https://objects-and-objecttypes-api.readthedocs.io/en/latest/installation/config.html>`_

.. warning::

    ``SECURE_HSTS_SECONDS`` has been added with a default of 31536000 seconds, ensure that
    before upgrading to this version of open-api-framework, your entire application is served
    over HTTPS, otherwise this setting can break parts of your application (see https://docs.djangoproject.com/en/4.2/ref/middleware/#http-strict-transport-security)

**Bugfixes and QOL**

* bumped python dependencies due to security issues: django, celery, certifi, maykin-2fa, mozilla-django-oidc-db,
  sentry-sdk, webob and others (#428)
* bumped ``zgw-consumers`` to 0.29.0 and updated a code for clients, because of zgw-consumers breaking change.
* paginated ``/api/v2/objects/{uuid}/history``endpoint (#329)
* fixed ``"register_kanalen`` command (#426)
* fixed notification page link (open-zaak/open-notificaties#171)

** Documentation**

* updated the documentation of environment variables using open-api-framework (open-zaak/open-zaak#1649)


2.4.1 (2024-08-06)
------------------

**Bugfixes and QOL**

* added Celery healthcheck
* made user emails unique to prevent two users logging in with the same email,
  causing an error

**Project maintenance**

* added CI-job to check for unexpected changes in the OAS (#420)

.. warning::

    User email addresses will now be unique on a database level. The database
    migration will fail if there are already two or more users with the same
    email address. You must ensure this is not the case before upgrading.

2.4.0 (2024-07-05)
------------------

**New features**

* added superuser permissions to API (#369)
* added `setup_configuration` management command which can configure API with
  environment variables (#368)
* added `Record.data` as a search filter in the Admin (#381)
* displayed `Objecttype.uuid` in the Objecttype and Object admin pages (#315)

**Bugfixes and QOL**

* supported `correctionFor` = `null` in POST/PUT requests (#268)
* added tests for `additionalProperties` keyword in JSON schema (#330)
* fixed creating objects with empty data (#371)
* fixed displaying the Token admin page if Object Types API is unavailable (#373)
* fixed styling of OIDC login page (#392)
* fixed styling of the help text icon in the Admin (#421)
* updated demo data used in quick start process (#398, #400)

**Project maintenance**

* updated Python to 3.11 (#379)
* added `open-api-framework` dependency (#358)
* refactored settings using `open-api-framework` (#413)
* added logging of outgoind requests (#344)
* added Trivy into the CI as an docker image scaner (#402)
* added GitHub issue templates (#389)
* merged quick start and regular docker compose files into one (#408)
* changed caching backend from LocMem to Redis
* Elastic APM service name can now be configured with ``ELASTIC_APM_SERVICE_NAME`` envvar

** Documentation**

* added security policy (#390)
* updated Quick start documentation (#348)

.. warning::

    Because the caching backend was changed to Redis, existing deployments must add a Redis container or Redis instance
    (see ``Installation > Environment configuration reference`` in the documentation on how to configure) the connection with Redis

.. warning::

    The service name for Elastic APM is now configurable via the ``ELASTIC_APM_SERVICE_NAME`` environment variable.
    The default value changed from ``Objects API`` to ``objects - <ENVIRONMENT>``


2.3.2 (2024-05-03)
------------------

Bugfix release

This release addresses a security weakness.

* [GHSA-3wcp-29hm-g82c] replaced PK for Token model.


2.3.1 (2024-03-22)
------------------

**Bugfixes and QOL**

* fixed celery docker container (#376)
* configured caches with redis (#377)
* added flower to monitor celery tasks (#378)

.. note::

    Flower is added to the docker, so now flower container could be deployed for monitoring
    purposes.


2.3.0 (2024-03-15)
------------------

* Updated to Django 4.2.

.. warning::

    Celery (and thus Redis) is now a required dependency.

    Two-factor authentication is enabled by default. The ``DISABLE_2FA`` environment variable
    can be used to disable it if needed.

2.2.1 (2024-03-02)
------------------

**Bugfixes and QOL**

* fixes OIDC config page by adding ``django_jsonform`` to ``INSTALLED_APPS`` (#350)
* added ``USE_X_FORWARDED_HOST`` environment variable (#353)
* added email environment variables (#366)


2.2.0 (2024-01-30)
------------------

**Component changes**

* **Bugfixes and QOL**

* fixed Permission form in the Admin (#309)
* added ``ENVIRONMENT`` environment variable (#310)
* updated python from 3.7 to 3.10 (#357)
* bumped Django to 3.2 (#357)
* bumped python libraries including mozilla-django-oidc, mozilla-django-oidc-db, zgw-consumers, uwsgi (#357, #338)
* removed hijack library (#357)
* updated base for docker image from Debian 10 to Debian 12 (#357)

**API 2.2.0 changes**

* **New features**

  * added `typeVersion` query parameter (#306)
  * supported JSON merge when doing a partial update on ``data`` attribute (#351)

* **Bugfixes**

  * added `typeVersion` query parameter (#306)
  * fixed date-time parsing in API filtering (#308)

.. warning::

   Change in deployment is required. `/media/` volume should be configured to share OAS files.

   Explanation:

   The new version of ``zgw_consumers`` library adds ``oas_file`` filed to ``Service`` model.
   This field saves OAS file into ``MEDIA_ROOT`` folder.
   The deployment now should have a volume for it.
   Please look at the example in ``docker-compose.yml``

2.1.1 (2022-06-24)
------------------

* **Bugfixes and QOL**

  * fixed updating objects with earlier `startAt` attribute (#282)
  * removed boostrap from the landing page (#294)
  * bumped to newer versions of pyjwt (#299)
  * fixed Elastic APM configuration (#289)


2.1.0 (2022-05-17)
------------------

**Component changes**

* **Bugfixes and QOL**

  * managed 2FA authentication using environment variables (#250)
  * integrated with OpenID Connect (#246)
  * create initial superuser with environment variables (#254)
  * removed non-actual results when filtering on `data_attr` query param (#260)
  * supported objecttypes with json schemas without properties in the Objects Admin (#273)
  * bumped to newer versions of mozilla-django-oidc-db (#264), django, lxml, babel, waitress(#293), pillow (#285) and npm packages (#279)
  * remove swagger2openapi from dependencies (#292)

* **Deployment tooling / infrastructure**

  * use ansible collections from Ansible Galaxy (#241)

**API 1.3.0 changes**

* **New features**

  * supported numeric values for `icontains` query param (#262)
  * supported validation on `hasGeometry` field in the Objecttypes API (#263)

**API 2.1.0 changes**

* **New features**

  * supported numeric values for `icontains` query param (#262)
  * supported validation on `hasGeometry` field in the Objecttypes API (#263)
  * supported `ordering` query param which allows to sort the results (#274)


2.0.0 (2021-09-22)
------------------

**Component changes**

* Supports API 2.0.0 and API 1.2.0

**API 1.2.0 changes**

* **New features**

  * supported having several API versions at the same time (#195)
  * enabled selecting set of fields for every object type version which are allowed to display in the API (#79)
  * sent notifications when the objects are changed in the API using Notificaties API. Sending notifications is an optional feature that can be disabled (#221, #237)
  * added an endpoint to show which API permissions the client has (#81)
  * made `geometry` field non-required for the `search` endpoint (#236)
  * supported dates in the `data_attrs=` query param (#214)
  * supported `icontains` operator in the `data_attrs=` query param, which allows case-insensitive search on the part of the string (#235)
  * added two-factor authentication for the Objects Admin (#232)

* **Bugfixes and QOL**

  * bumped to newer versions of django, django-debug-toolbar, urllib3, sqlparse (#225, #243)
  * added superuser for quick-start (#203)
  * tested the performance of the API per version (#219)

* **Documentation**

  * marked read-only fields as non-required in OAS (#210)
  * described how to configure authorization with the set of allowed fields in the admin (#79)
  * documented how to configure notifications (#245)

**API 2.0.0 changes**

* **Breaking features**

  * paginated API responses (#148)

* **New features**

  * supported `data_icontains` query param which requires Postgres 12+ (#235)

* **Deployment tooling / infrastructure**

  * updated Postgres version in the Objects API Helm chart (#242)


1.1.1 (2021-06-22)
------------------

**Bugfixes and QOL**

* Fixed OAS generation: remove unrelated error response bodies and headers, swap the notion of material and formal history (#197, #201)
* Tested the implementation of the material and formal history (#168)

**Documentation**

* Documented how to use the Objecttypes admin and the Objects admin (#60)


1.1.0 (2021-04-21)
------------------

**New features**

* Decoupled authentication tokens from users in the admin (#115)
* Added additional fields for tokens to store extra information (#155)
* Adhered the Objecttypes API to API principles API-09, API-18, API-19, API-51 defined in API Design Rules of Nederlandse API Strategie (#46, #174)
* Supported `fields=` query param and display only selected fields in the API response (#174)
* Added length validation fo url fields (#154)
* Improved the Admin UI:

  * Include `uuid` field to the "object" page (#156)
  * Make `object_type` field immutable (#150)
  * Add filtering on `object_type` to the "object" page (#157)

**Bugfixes and QOL**

* Improved performance with database query optimization (#136) :zap:
* Bumped to newer versions of Django, Jinja2, Pillow, PyYAML, pip-tools including security fixes (#183, #182, #184, #176, #193)
* Fixed a crash when creating an object without a version in the admin (#146)

**Deployment tooling / infrastructure**

* Added Helm chart to deploy the Objects API on Kubernetes (#180)
* Added Ansible configuration to deploy the Objects API on single server (#59)

**Documentation**

* Added a tutorial how to use the Objects API and the Objecttypes API with examples (#61)
* Documented how to configure authentication and authorization for the Objects API and the Objecttypes API (#179)
* Documented deployment of the Objects API and the Objecttypes API on single server and Kubernetes (#59)
* Translated descriptions for `Content-Crs` and `Accept-Crs` headers from Dutch to English in the OAS (#106)
* Added information about validation to the OAS (#106)


1.0.0 (2021-01-13)
------------------

🎉 First release of Objects API.
