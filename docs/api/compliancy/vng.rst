.. _compliancy_vng:

==============
VNG compliancy
==============

The Objects and Objecttypes API specifications are proposed by the `municipality
of Utrecht`_ and submitted to the `VNG`_ for to become a Dutch national
standard. The VNG (Vereniging van Nederlandse Gemeenten) is the Association of
Dutch Municipalities.

The VNG has drafted an initial checklist for new API standards which is shown
in the table below. The table below also shows the compliancy to this checklist
for both APIs. This checklist is only available in Dutch.

.. csv-table:: 1. Stakeholder documentatie
   :header: "#"; "Description"; "Answer"; "Remarks"
   :widths: 5, 55, 15, 25
   :delim: ;

   1;De voor de stakeholders relevante onderdelen van de standaard (informatiemodel, API-specificaties, functionele specificatie, architectuurmodellen, referentieimplementatie(s) en testgevallen) zijn gepubliceerd op de VNG Realisatie Github of GEMMAonline omgeving.;No [1]_;
   2;Er is een beschrijving die ontwikkelaars op weg helpt om te starten met implementatie van de API-standaard.;`Yes <https://objects-and-objecttypes-api.readthedocs.io/en/latest/>`__;
   3;Er is uitleg en installatie-instructies van de referentieimplementaties;`Yes <https://objects-and-objecttypes-api.readthedocs.io/en/latest/installation/quickstart.html>`__;
   4;Er is uitleg over hoe mee ontwikkeld kan worden aan de referentieimplementatie(s), inclusief gebruik van relevante tooling.;`Yes <https://github.com/maykinmedia/objects-api/blob/master/CONTRIBUTING.md>`__;
   5;Er zijn Postman-scripts met voorbeelden zodat consumers snel kunnen leren hoe ze de API moeten aanroepen.;`Yes <https://objects-and-objecttypes-api.readthedocs.io/en/latest/api/postman.html>`__;
   6;VNG-site, API-ontwikkelagenda;Yes;No link available.

.. csv-table:: 2. Informatiemodel
   :header: "#"; "Description"; "Answer"; "Remarks"
   :widths: 5, 55, 15, 25
   :delim: ;

   1;Indien gemeentelijke bron dan opleveren informatiemodel (semantisch informatiemodel);`Yes <https://objects-and-objecttypes-api.readthedocs.io/en/latest/introduction/information-model.html>`__;
   2;Altijd een uitwisselingsgegevensmodel;No;
   3;Modellering van het semantisch informatiemodel conform laatst vastgestelde versie Metamodel Informatiemodellen (MIM);Yes;See 2.1.
   4;Informatiemodel gemodelleerd in Enterprise Architect conform de daarvoor geldende best practices;Yes;See 2.1.
   5;Informatiemodel is opgeslagen in SVN;No [1]_;

.. csv-table:: 3. Architectuur
   :header: "#"; "Description"; "Answer"; "Remarks"
   :widths: 5, 55, 15, 25
   :delim: ;

   1;Modellen zijn gemodelleerd in Archi (Archimate 3.x) conform conventies GEMMA;No;Unclear
   2;Modellen zijn opgeslagen op GitLab / Github en ingericht voor samenwerking (main/develop branches);No;
   3;De stakeholders van de API-standaard zijn beschreven;`Yes <https://objects-and-objecttypes-api.readthedocs.io/en/latest/introduction/team.html>`__;
   4;Interactiepatronen zijn gemodelleerd;Yes;
   5;Positie van de API-standaard in de GEMMA informatiearchitectuur is gemodelleerd;No;Unclear
   6;Verwacht gedrag van een API is gemodelleerd als applicatieproces;No;Unclear
   7;De referentiecomponenten die het koppelvlak moeten realiseren zijn beschreven;`Yes <https://objects-and-objecttypes-api.readthedocs.io/en/latest/api/index.html>`__;
   8;Per referentiecomponent is beschreven welke verplicht dan wel optioneel te leveren (provider) of te gebruiken (consumer) services en operaties geïmplementeerd moeten zijn om compliant aan de standaard te zijn.;`Yes <https://objects-and-objecttypes-api.readthedocs.io/en/latest/api/index.html>`__;

.. csv-table:: 4. API-specificaties
   :header: "#"; "Description"; "Answer"; "Remarks"
   :widths: 5, 55, 15, 25
   :delim: ;

   1;Opgesteld in Open API Specification 3.x;`Yes <https://objects-and-objecttypes-api.readthedocs.io/en/latest/api/index.html>`__;
   2;Gepubliceerd op VNG-Realisatie Github omgeving en beschikbaar via Redoc en Swagger;No [1]_;
   3;Ontwerpbeslissing zijn vertaald naar (aanvullende) specificaties;`Yes <https://github.com/maykinmedia/objects-api/issues>`_;
   4;Voldoet aan landelijke API strategie, in het bijzonder de core design rules;`Yes <https://objects-and-objecttypes-api.readthedocs.io/en/latest/api/compliancy/api-strategy.html>`__;
   5;Informatiebeveiliging en privacy best practices (IBD) worden gevolgd;No;Unclear
   6;Aanvullende specificaties die het gedrag van de API specificeren voor de provider.;No;TODO
   7;De OAS3-specificatie is getest voor toepasbaarheid in de mainstream code-generatoren;Yes (`1 <https://github.com/maykinmedia/objects-api/actions?query=workflow%3Agenerate-sdks>`__, `2 <https://github.com/maykinmedia/objecttypes-api/actions?query=workflow%3Agenerate-sdks>`__);
   8;API-specificaties volgen de VNG-R best practices.;No;There are no VNG-R best practices.

.. csv-table:: 5. Compliancy en testen
   :header: "#"; "Description"; "Answer"; "Remarks"
   :widths: 5, 55, 15, 25
   :delim: ;

   1;API-standaard is geïmplementeerd in een referentieimplementatie indien voor de standaard meerdere providers van toepassing kunnen zijn;Yes (`1 <https://github.com/maykinmedia/objects-api/>`__, `2 <https://github.com/maykinmedia/objecttypes-api/>`__);
   2;Testgevallen zijn beschreven voor elke service/operatie en aanvullende specificaties, zowel voor de happy als de unhappy flows;Yes (`1 <https://github.com/maykinmedia/objects-api/actions>`__, `2 <https://github.com/maykinmedia/objecttypes-api/actions>`__);
   3;Elk testgeval beschrijft het logische testgeval, de teststap(pen) (wat wordt gedaan) en het verwachte resultaat;No;Unclear
   4;Er zijn compliancy tests beschikbaar voor elke referentie-component (consumers en providers) en alle betreffende services en operaties, zodat leveranciers kunnen testen en aantonen dat hun applicatie voldoet aan de standaard;No;TODO
   5;Voor zover nodig is ook de testdata beschreven die wordt gebruikt in de testgevallen;No;See 5.4.
   6;Testgevallen zijn geïmplementeerd als Postman-scripts zodat de API geautomatiseerd getest kan worden.;No;See 5.4.
   7;Postman-scripts zijn gepubliceerd op api-test.nl zodat iedereen kan testen of de API voldoet aan zijn specificatie.;No;See 5.4.

.. csv-table:: 6. Referentie-implementatie
   :header: "#"; "Description"; "Answer"; "Remarks"
   :widths: 5, 55, 15, 25
   :delim: ;

   1;Zowel consumer als provider implementatie. Provider alleen van toepassing als meerdere providers mogelijk zijn. Minimaal zorgen voor test-implementatie;Yes (`1 <https://github.com/maykinmedia/objects-api/>`__, `2 <https://github.com/maykinmedia/objecttypes-api/>`__); Same as 5.1.
   2;Implementeert de OAS-specificatie inclusief de eventueel gedefinieerde aanvullende specificatie;Yes;Unsure how to provide proof.
   3;Is voldoende functioneel om implementatie en gebruik van de API-standaard te demonstreren en compliancy aan te tonen;Yes;Unsure how to provide proof.

.. csv-table:: 7. Overdrachtsdocument (beheer)
   :header: "#"; "Description"; "Answer"; "Remarks"
   :widths: 5, 55, 15, 25
   :delim: ;

   1;De genomen ontwerpbeslissingen zijn beschreven en gemotiveerd;`Yes <https://github.com/maykinmedia/objects-api/issues>`__;
   2;Er is een lijst met bekende fouten, gewenste verbeteringen, gewenste uitbreidingen (backlog);`Yes <https://github.com/maykinmedia/objects-api/issues>`__;
   3;Er wordt voldaan aan de acceptatie criteria van de beheer organisatie die de standaard in beheer neemt;Yes;This checklist.
   4;Beheerafspraken zijn beschreven;No;Unclear

.. [1] This is most likely an internal VNG compliancy check and is considered out of scope.

.. _`municipality of Utrecht`: https://www.utrecht.nl/
.. _`VNG`: https://vng.nl/
