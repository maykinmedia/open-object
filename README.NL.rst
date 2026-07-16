============
Objecten API
============

:Version: 2.5.1
:Source: https://github.com/maykinmedia/objecttypes-api
:Keywords: objecten, assets, zaakobjecten

|docs|

API om objecten te beheren die behoren bij een bepaald objecttype.
(`English version`_)

Ontwikkeld door `Maykin Media B.V.`_ in opdracht van de gemeente Utrecht.


Introductie
===========

De Objecten API heeft als doel om uiteenlopende objecten eenvoudig te kunnen
registreren en ontsluiten in een gestandaardiseerd formaat. De Objecten API kan
door elke organisatie ingezet worden om de voor haar interessante objecten te
beheren. Ook kan een organisatie er voor kiezen een Objecten API in te zetten
voor Open Data, waarbij de geregistreerde objecten publiekelijk toegankelijk
zijn.

Om het formaat van objecten, de zogenoemde objecttypen, vast te leggen wordt
gebruik gemaakt van de landelijke en/of een lokale `Objecttypen API`_.


API specificatie
================

|lint-oas| |generate-sdks| |generate-postman-collection|

==============  ==============  =============================
Versie          Release datum   API specificatie
==============  ==============  =============================
latest          n/a             `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/master/src/objects/api/v2/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/master/src/objects/api/v2/openapi.yaml>`_,
                                (`verschillen <https://github.com/maykinmedia/objects-api/compare/2.5.1..master>`_)
2.5.1           2026-07-16      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/2.5.1/src/objects/api/v2/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/2.5.1/src/objects/api/v2/openapi.yaml>`_
                                (`verschillen <https://github.com/maykinmedia/objects-api/compare/2.5.0..2.5.1>`_)
2.5.0           2025-01-10      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/2.5.0/src/objects/api/v2/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/2.5.0/src/objects/api/v2/openapi.yaml>`_
                                (`verschillen <https://github.com/maykinmedia/objects-api/compare/2.4.3..2.5.0>`_)
2.4.4           2024-03-22      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/2.4.4/src/objects/api/v2/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/2.4.4/src/objects/api/v2/openapi.yaml>`_
                                (`verschillen <https://github.com/maykinmedia/objects-api/compare/2.4.3..2.4.4>`_)
2.4.3           2024-03-22      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/2.4.3/src/objects/api/v2/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/2.4.3/src/objects/api/v2/openapi.yaml>`_
                                (`verschillen <https://github.com/maykinmedia/objects-api/compare/2.3.0..2.4.3#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
2.3.0           2024-03-15      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/2.3.0/src/objects/api/v2/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/2.3.0/src/objects/api/v2/openapi.yaml>`_
                                (`verschillen <https://github.com/maykinmedia/objects-api/compare/2.2.1..2.3.0#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
2.2.1           2024-01-30      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/2.2.1/src/objects/api/v2/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/2.2.1/src/objects/api/v2/openapi.yaml>`_
                                (`verschillen <https://github.com/maykinmedia/objects-api/compare/2.1.1..2.2.1#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
2.1.0           2022-06-24      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/2.1.1/src/objects/api/v2/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/2.1.1/src/objects/api/v2/openapi.yaml>`_
                                (`verschillen <https://github.com/maykinmedia/objects-api/compare/2.1.0..2.1.1#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
2.1.0           2022-05-17      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/2.1.0/src/objects/api/v2/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/2.1.0/src/objects/api/v2/openapi.yaml>`_
                                (`verschillen <https://github.com/maykinmedia/objects-api/compare/2.0.0..2.1.0#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
2.0.0           2021-09-22      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/2.0.0/src/objects/api/v2/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/2.0.0/src/objects/api/v2/openapi.yaml>`_
                                (`verschillen <https://github.com/maykinmedia/objects-api/compare/1.2.0..2.0.0#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
1.3.0           2021-01-12      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/1.3.0/src/objects/api/v1/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/1.3.0/src/objects/api/v1/openapi.yaml>`_
                                (`verschillen <https://github.com/maykinmedia/objects-api/compare/1.2.0..1.3.0#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
1.2.0           2021-09-22      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/1.2.0/src/objects/api/v1/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/1.2.0/src/objects/api/v1/openapi.yaml>`_
                                (`verschillen <https://github.com/maykinmedia/objects-api/compare/1.1.1..1.2.0#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
1.1.1           2021-06-22      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/1.1.1/src/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/1.1.1/src/openapi.yaml>`_
                                (`verschillen <https://github.com/maykinmedia/objects-api/compare/1.1.0..1.1.1#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
1.1.0           2021-04-21      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/1.1.0/src/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/1.1.0/src/openapi.yaml>`_
                                (`verschillen <https://github.com/maykinmedia/objects-api/compare/1.0.0..1.1.0#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
1.0.0           2021-01-13      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/1.0.0/src/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/1.0.0/src/openapi.yaml>`_
==============  ==============  =============================

Vorige versies worden nog 6 maanden ondersteund nadat de volgende versie is uitgebracht.

Zie: `Alle versies en wijzigingen <https://github.com/maykinmedia/objects-api/blob/master/CHANGELOG.rst>`_


Referentie implementatie
========================

|build-status| |coverage| |black| |docker| |python-versions|

De referentie implementatie toont de API in actie en kan gebruikt worden voor
test en demonstratie doeleinden. De referentie implementatie is open source,
goed getest en beschikbaar als Docker image.

Quickstart
----------

1. Download en start de Objecten API:

   .. code:: bash

      wget https://raw.githubusercontent.com/maykinmedia/objects-api/master/docker-compose.yml
      docker compose up -d --no-build
      docker compose exec web src/manage.py loaddata demodata
      docker compose exec web src/manage.py createsuperuser

2. In de browser, navigeer naar ``http://localhost:8000/`` om de admin en de
   API te benaderen.


Links
=====

* `Documentatie <https://objects-and-objecttypes-api.readthedocs.io/>`_
* `Docker image <https://hub.docker.com/r/maykinmedia/objects-api>`_
* `Issues <https://github.com/maykinmedia/objects-api/issues>`_
* `Code <https://github.com/maykinmedia/objects-api>`_
* `Community <https://commonground.nl/groups/view/54477963/objecten-en-objecttypen-api>`_


Licentie
========

Copyright © Maykin Media, 2020 - 2021

Licensed under the EUPL_


.. _`English version`: README.rst

.. _`Maykin Media B.V.`: https://www.maykinmedia.nl

.. _`Objecttypen API`: https://github.com/maykinmedia/objecttypes-api

.. _`EUPL`: LICENSE.md

.. |build-status| image:: https://github.com/maykinmedia/objects-api/workflows/ci/badge.svg?branch=master
    :alt: Build status
    :target: https://github.com/maykinmedia/objects-api/actions?query=workflow%3Aci

.. |docs| image:: https://readthedocs.org/projects/objects-and-objecttypes-api/badge/?version=latest
    :target: https://objects-and-objecttypes-api.readthedocs.io/
    :alt: Documentation Status

.. |coverage| image:: https://codecov.io/github/maykinmedia/objects-api/branch/master/graphs/badge.svg?branch=master
    :alt: Coverage
    :target: https://codecov.io/gh/maykinmedia/objects-api

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :alt: Code style
    :target: https://github.com/psf/black

.. |docker| image:: https://images.microbadger.com/badges/image/maykinmedia/objects-api.svg
    :alt: Docker image
    :target: https://hub.docker.com/r/maykinmedia/objects-api

.. |python-versions| image:: https://img.shields.io/badge/python-3.7%2B-blue.svg
    :alt: Supported Python version

.. |lint-oas| image:: https://github.com/maykinmedia/objects-api/workflows/lint-oas/badge.svg
    :alt: Lint OAS
    :target: https://github.com/maykinmedia/objects-api/actions?query=workflow%3Alint-oas

.. |generate-sdks| image:: https://github.com/maykinmedia/objects-api/workflows/generate-sdks/badge.svg
    :alt: Generate SDKs
    :target: https://github.com/maykinmedia/objects-api/actions?query=workflow%3Agenerate-sdks

.. |generate-postman-collection| image:: https://github.com/maykinmedia/objects-api/workflows/generate-postman-collection/badge.svg
    :alt: Generate Postman collection
    :target: https://github.com/maykinmedia/objects-api/actions?query=workflow%3Agenerate-postman-collection
