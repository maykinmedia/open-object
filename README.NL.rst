=============
Open Object
=============

:Version: 4.0.1
:Source: https://github.com/maykinmedia/open-object
:Keywords: objecten, assets, zaakobjecten

|docs|

API om objecten te beheren die behoren bij een bepaald objecttype.
(`English version`_)

Ontwikkeld door `Maykin Media B.V.`_ in opdracht van de gemeente Utrecht.


Introductie
===========

Open Object heeft als doel om uiteenlopende typen objecten op een dynamische wijze te standaardiseren en om te voorkomen dat
voor elk (eenvoudig) object een volledige API wordt opgezet. instanties van objecten kunnen eenvouding worden geregistreerd en
ontsloten in een gestandaardiseerd formaat. De Objecten API kan door elke organisatie ingezet worden om de voor haar interessante objecten te
beheren. Ook kan een organisatie er voor kiezen een Objecten API in te zetten voor Open Data, waarbij de geregistreerde objecten publiekelijk toegankelijk
zijn.


API specificatie
================

|lint-oas| |generate-sdks| |generate-postman-collection|

=================       ==============  =============================
Applicatie versie       Release datum   API specificatie
=================       ==============  =============================
latest                  n/a             `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-object/master/src/objects/api/v2/openapi.yaml>`_,
                                        `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-object/master/src/objects/api/v2/openapi.yaml>`_,
                                        (`verschillen <https://github.com/maykinmedia/open-object/compare/4.0.1..master>`_)
4.0.1                   2026-05-22      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-object/4.0.1/src/objects/api/v2/openapi.yaml>`_,
                                        `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-object/4.0.1/src/objects/api/v2/openapi.yaml>`_
                                        (`verschillen <https://github.com/maykinmedia/open-object/compare/4.0.0..4.0.1>`_)
4.0.0                   2026-04-13      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-object/4.0.0/src/objects/api/v2/openapi.yaml>`_,
                                        `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-object/4.0.0/src/objects/api/v2/openapi.yaml>`_
                                        (`verschillen <https://github.com/maykinmedia/open-object/compare/3.6.1..4.0.0>`_)
3.6.1                   2026-05-22      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.6.1/src/objects/api/v2/openapi.yaml>`_,
                                        `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.6.1/src/objects/api/v2/openapi.yaml>`_
                                        (`verschillen <https://github.com/maykinmedia/open-object/compare/3.6.0..3.6.1>`_)
3.6.0                   2026-02-06      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.6.0/src/objects/api/v2/openapi.yaml>`_,
                                        `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.6.0/src/objects/api/v2/openapi.yaml>`_
                                        (`verschillen <https://github.com/maykinmedia/open-object/compare/3.5.0..3.6.0>`_)
3.5.0                   2025-12-01      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.5.0/src/objects/api/v2/openapi.yaml>`_,
                                        `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.5.0/src/objects/api/v2/openapi.yaml>`_
                                        (`verschillen <https://github.com/maykinmedia/open-object/compare/3.4.0..3.5.0>`_)
3.4.0                   2025-10-28      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.4.0/src/objects/api/v2/openapi.yaml>`_,
                                        `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.4.0/src/objects/api/v2/openapi.yaml>`_
                                        (`verschillen <https://github.com/maykinmedia/open-object/compare/3.3.1..3.4.0>`_)
3.3.1                   2025-10-16      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.3.1/src/objects/api/v2/openapi.yaml>`_,
                                        `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.3.1/src/objects/api/v2/openapi.yaml>`_
                                        (`verschillen <https://github.com/maykinmedia/open-object/compare/3.3.0..3.3.1>`_)
3.3.0                   2025-10-02      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.3.0/src/objects/api/v2/openapi.yaml>`_,
                                        `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.3.0/src/objects/api/v2/openapi.yaml>`_
                                        (`verschillen <https://github.com/maykinmedia/open-object/compare/3.2.0..3.3.0>`_)
3.2.0                   2025-09-16      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.2.0/src/objects/api/v2/openapi.yaml>`_,
                                        `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.2.0/src/objects/api/v2/openapi.yaml>`_
                                        (`verschillen <https://github.com/maykinmedia/open-object/compare/3.1.4..3.2.0>`_)
3.1.4                   2025-08-28      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.1.4/src/objects/api/v2/openapi.yaml>`_,
                                        `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.1.4/src/objects/api/v2/openapi.yaml>`_
                                        (`verschillen <https://github.com/maykinmedia/open-object/compare/3.1.3..3.1.4>`_)
3.1.3                   2025-08-04      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.1.3/src/objects/api/v2/openapi.yaml>`_,
                                        `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.1.3/src/objects/api/v2/openapi.yaml>`_
                                        (`verschillen <https://github.com/maykinmedia/open-object/compare/3.1.2..3.1.3>`_)
3.1.2                   2025-07-22      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.1.2/src/objects/api/v2/openapi.yaml>`_,
                                        `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.1.2/src/objects/api/v2/openapi.yaml>`_
                                        (`verschillen <https://github.com/maykinmedia/open-object/compare/3.1.1..3.1.2>`_)
3.1.1                   2025-07-04      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.1.1/src/objects/api/v2/openapi.yaml>`_,
                                        `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.1.1/src/objects/api/v2/openapi.yaml>`_
                                        (`verschillen <https://github.com/maykinmedia/open-object/compare/3.1.0..3.1.1>`_)
3.1.0                   2025-05-26      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.1.0/src/objects/api/v2/openapi.yaml>`_,
                                        `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.1.0/src/objects/api/v2/openapi.yaml>`_
                                        (`verschillen <https://github.com/maykinmedia/open-object/compare/3.0.4..3.1.0>`_)
3.0.4                   2025-05-13      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.0.4/src/objects/api/v2/openapi.yaml>`_,
                                        `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.0.4/src/objects/api/v2/openapi.yaml>`_
                                        (`verschillen <https://github.com/maykinmedia/open-object/compare/3.0.3..3.0.4>`_)
3.0.3                   2025-04-03      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.0.3/src/objects/api/v2/openapi.yaml>`_,
                                        `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.0.3/src/objects/api/v2/openapi.yaml>`_
                                        (`verschillen <https://github.com/maykinmedia/open-object/compare/3.0.2..3.0.3>`_)
3.0.2                   2025-03-07      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.0.2/src/objects/api/v2/openapi.yaml>`_,
                                        `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.0.2/src/objects/api/v2/openapi.yaml>`_
                                        (`verschillen <https://github.com/maykinmedia/open-object/compare/3.0.1..3.0.2>`_)
3.0.1                   2025-03-04      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.0.1/src/objects/api/v2/openapi.yaml>`_,
                                        `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.0.1/src/objects/api/v2/openapi.yaml>`_
                                        (`verschillen <https://github.com/maykinmedia/open-object/compare/3.0.0..3.0.1>`_)
3.0.0                   2025-01-22      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.0.0/src/objects/api/v2/openapi.yaml>`_,
                                        `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-object/3.0.0/src/objects/api/v2/openapi.yaml>`_
                                        (`verschillen <https://github.com/maykinmedia/open-object/compare/2.5.0..3.0.0>`_)
2.5.0                   2025-01-09      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-object/2.5.0/src/objects/api/v2/openapi.yaml>`_,
                                        `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-object/2.5.0/src/objects/api/v2/openapi.yaml>`_
                                        (`verschillen <https://github.com/maykinmedia/open-object/compare/2.4.3..2.5.0>`_)
2.4.4                   2024-03-22      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-object/2.4.4/src/objects/api/v2/openapi.yaml>`_,
                                        `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-object/2.4.4/src/objects/api/v2/openapi.yaml>`_
                                        (`verschillen <https://github.com/maykinmedia/open-object/compare/2.4.3..2.4.4>`_)
2.4.3                   2024-03-22      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-object/2.4.3/src/objects/api/v2/openapi.yaml>`_,
                                        `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-object/2.4.3/src/objects/api/v2/openapi.yaml>`_
                                        (`verschillen <https://github.com/maykinmedia/open-object/compare/2.3.0..2.4.3#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
2.3.0                   2024-03-15      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-object/2.3.0/src/objects/api/v2/openapi.yaml>`_,
                                        `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-object/2.3.0/src/objects/api/v2/openapi.yaml>`_
                                        (`verschillen <https://github.com/maykinmedia/open-object/compare/2.2.1..2.3.0#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
2.2.1                   2024-01-30      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-object/2.2.1/src/objects/api/v2/openapi.yaml>`_,
                                        `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-object/2.2.1/src/objects/api/v2/openapi.yaml>`_
                                        (`verschillen <https://github.com/maykinmedia/open-object/compare/2.1.1..2.2.1#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
2.1.0                   2022-06-24      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-object/2.1.1/src/objects/api/v2/openapi.yaml>`_,
                                        `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-object/2.1.1/src/objects/api/v2/openapi.yaml>`_
                                        (`verschillen <https://github.com/maykinmedia/open-object/compare/2.1.0..2.1.1#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
2.1.0                   2022-05-17      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-object/2.1.0/src/objects/api/v2/openapi.yaml>`_,
                                        `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-object/2.1.0/src/objects/api/v2/openapi.yaml>`_
                                        (`verschillen <https://github.com/maykinmedia/open-object/compare/2.0.0..2.1.0#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
2.0.0                   2021-09-22      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-object/2.0.0/src/objects/api/v2/openapi.yaml>`_,
                                        `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-object/2.0.0/src/objects/api/v2/openapi.yaml>`_
                                        (`verschillen <https://github.com/maykinmedia/open-object/compare/1.2.0..2.0.0#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
=================       ==============  =============================

Vorige versies worden nog 6 maanden ondersteund nadat de volgende versie is uitgebracht.

Zie: `Alle versies en wijzigingen <https://github.com/maykinmedia/open-object/blob/master/CHANGELOG.rst>`_


Referentie implementatie
========================

|build-status| |coverage| |code-style| |codeql| |ruff| |docker| |python-versions|

De referentie implementatie toont de API in actie en kan gebruikt worden voor
test en demonstratie doeleinden. De referentie implementatie is open source,
goed getest en beschikbaar als Docker image.

Quickstart
----------

1. Download en start Open Object:

   .. code:: bash

      wget https://raw.githubusercontent.com/maykinmedia/open-object/master/docker-compose.yml
      docker compose up -d --no-build
      docker compose exec web src/manage.py loaddata demodata
      docker compose exec web src/manage.py createsuperuser

2. In de browser, navigeer naar ``http://localhost:8000/`` om de admin en de
   API te benaderen.


Links
=====

* `Documentatie <https://open-object.readthedocs.io/>`_
* `Docker image <https://hub.docker.com/r/maykinmedia/open-object>`_
* `Issues <https://github.com/maykinmedia/open-object/issues>`_
* `Code <https://github.com/maykinmedia/open-object>`_
* `Community <https://commonground.nl/groups/view/54477963/objecten-en-objecttypen-api>`_


Licentie
========

Copyright © Maykin Media, 2020 - 2021

Licensed under the EUPL_


.. _`English version`: README.rst

.. _`Maykin Media B.V.`: https://www.maykinmedia.nl

.. _`EUPL`: LICENSE.md

.. |build-status| image:: https://github.com/maykinmedia/open-object/workflows/ci/badge.svg?branch=master
    :alt: Build status
    :target: https://github.com/maykinmedia/open-object/actions?query=workflow%3Aci

.. |docs| image:: https://readthedocs.org/projects/open-object/badge/?version=latest
    :target: https://open-object.readthedocs.io/
    :alt: Documentation Status

.. |coverage| image:: https://codecov.io/github/maykinmedia/open-object/branch/master/graphs/badge.svg?branch=master
    :alt: Coverage
    :target: https://codecov.io/gh/maykinmedia/open-object

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Ruff

.. |code-style| image:: https://github.com/maykinmedia/open-object/actions/workflows/code-quality.yml/badge.svg?branch=master
    :alt: Code style
    :target: https://github.com/maykinmedia/open-object/actions/workflows/code-quality.yml

.. |codeql| image:: https://github.com/maykinmedia/open-object/actions/workflows/codeql-analysis.yml/badge.svg?branch=master
    :alt: CodeQL scan
    :target: https://github.com/maykinmedia/open-object/actions/workflows/codeql-analysis.yml

.. |docker| image:: https://img.shields.io/docker/v/maykinmedia/open-object.svg?sort=semver
    :alt: Docker image
    :target: https://hub.docker.com/r/maykinmedia/open-object

.. |python-versions| image:: https://img.shields.io/badge/python-3.12%2B-blue.svg
    :alt: Supported Python version

.. |lint-oas| image:: https://github.com/maykinmedia/open-object/workflows/lint-oas/badge.svg
    :alt: Lint OAS
    :target: https://github.com/maykinmedia/open-object/actions?query=workflow%3Alint-oas

.. |generate-sdks| image:: https://github.com/maykinmedia/open-object/workflows/generate-sdks/badge.svg
    :alt: Generate SDKs
    :target: https://github.com/maykinmedia/open-object/actions?query=workflow%3Agenerate-sdks

.. |generate-postman-collection| image:: https://github.com/maykinmedia/open-object/workflows/generate-postman-collection/badge.svg
    :alt: Generate Postman collection
    :target: https://github.com/maykinmedia/open-object/actions?query=workflow%3Agenerate-postman-collection
