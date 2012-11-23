mytardis-app-repos-producer
===========================


Hooks for MyTardis to allow upstream instances to ingest public experiments.

Installation
------------

Clone into the MyTardis ``APPS`` directory as normal

Configuring
-----------

Added to the settigs.py ``OAIPMH_PROVIDERS``.  For example::

  OAIPMH_PROVIDERS = [
  #    'tardis.apps.oaipmh.provider.experiment.DcExperimentProvider',
      'tardis.apps.oaipmh.provider.experiment.RifCsExperimentProvider',
      'tardis.apps.reposproducer.experiment.FederatedExperimentProvider',

  ]

Add application ``INSTALLED_APPS``.  For example::

  INSTALLED_APPS = (
    ...
    'tardis.apps.reposproducer'
    ...
    )