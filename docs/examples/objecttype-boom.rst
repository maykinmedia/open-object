.. _examples_objecttype-boom:

===========
Boom (Tree)
===========

The "Boom" objecttype is based on the open source `Gemeentelijk Gegevensmodel`_
(GGM) which in turn is based on the `Informatiemodel Beheer Openbare Ruimte`_
(IMBOR) which is a collection of the `Basisregistratie Grootschalige Topografie`_
(BGT) and the `Informatiemodel geografie`_ (IMGeo).

A `small script`_ was used to convert the GGM EAP model to JSON schema.

.. _`Gemeentelijk Gegevensmodel`: https://github.com/Gemeente-Delft/Gemeentelijk-Gegevensmodel
.. _`Informatiemodel Beheer Openbare Ruimte`: https://www.crow.nl/Onderwerpen/assetmanagement-en-beheer-openbare-ruimte/Data-en-informatie/imbor-de-standaard-voor-beheer-van-de-openbare-ruimte
.. _`Basisregistratie Grootschalige Topografie`: https://www.kadaster.nl/zakelijk/registraties/basisregistraties/bgt
.. _`Informatiemodel geografie`: https://www.geonovum.nl/geo-standaarden/bgt-imgeo
.. _`small script`: https://github.com/maykinmedia/imvertor-lite

Metadata
========

========================   ==========================
Attribute                  Value
========================   ==========================
name                       boom
namePlural                 bomen
description
labels
maintainerOrganization     Gemeente Delft
maintainerDepartment
contactPerson              Ashkan Ashkpour
contactEmail               aashkpour@delft.nl
providerOrganization
source
status                     draft
dataClassification         open
createdAt                  August 27, 2020
modifiedAt
publishedAt
updateFrequency
documentationUrl
========================   ==========================

Schema
======

You can download the JSON schema :download:`boom.json <_assets/boom.json>` or
view it below:

.. include:: _assets/boom.json
   :code: json
