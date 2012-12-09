mytardis-app-repos-producer
===========================


Hooks for MyTardis to allow upstream instances to ingest public experiments.

Installation
------------

Clone into the MyTardis ``APPS`` directory as ``reposconsumer``
e.g., ``git clone https://github.com/ianedwardthomas/mytardis-app-repos-producer reposproducer``

Configuring
-----------

Added to the settings.py ``OAIPMH_PROVIDERS``.  For example::

    OAIPMH_PROVIDERS = [
      #'tardis.apps.oaipmh.provider.experiment.DcExperimentProvider',
      'tardis.apps.oaipmh.provider.experiment.RifCsExperimentProvider',
      'tardis.apps.reposproducer.experiment.FederatedExperimentProvider',

    ]

Add application ``INSTALLED_APPS``.  For example::

    INSTALLED_APPS += ("tardis.apps.reposproducer", "tardis.apps.oaipmh")

Ensure that Sites model has valid entry.

Add unique key entry to settings.py::

    KEY_NAME = "experiment_key"
    KEY_NAMESPACE = "http://tardis.edu.au/schemas/experimentkey"

Finally add the corresponding schema and parametername using the admin tool

