.. _installation_prerequisites:

Prerequisites
=============

Open Object is most often deployed as a Docker container. While the
`Open Object container images <https://hub.docker.com/r/maykinmedia/open-object/>`_ contain all the
necessary dependencies, it requires extra services to deploy the full stack.
These dependencies and their supported versions are documented here.

The ``docker-compose.yml`` (not suitable for production usage!) in the root of the
repository also describes these dependencies.

PostgreSQL with Postgis
-----------------------

Open Object currently only supports PostgreSQL as datastore and is is geo-capable,
which requires the postgis_ extension to be enabled.

The supported versions in the table below are tested in the CI pipeline.

============ ==================== ============ ============ ============ ============
Matrix       Postgres 14 or lower Postgres 15  Postgres 16  Postgres 17  Postgres 18
============ ==================== ============ ============ ============ ============
Postgis 3.6  |cross|              |check|      |check|      |check|      |check|
Postgis 3.7  |cross|              |check|      |check|      |check|      |check|
============ ==================== ============ ============ ============ ============

.. warning:: only maintained versions of PostgreSQL are supported. Once a version is
   `EOL <https://www.postgresql.org/support/versioning/>`_, support will
   be dropped in the next release.

.. _postgis: https://postgis.net/

Redis
-----

Both components use Redis as a cache backend, especially relevant for admin sessions, and as
task queue broker.

Supported versions: 5, 6, 7.

.. |check| unicode:: U+2705 .. ✅
.. |cross| unicode:: U+274C .. ❌
