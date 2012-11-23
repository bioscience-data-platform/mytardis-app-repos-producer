from tardis.apps.oaipmh.provider.experiment import DcExperimentProvider

from oaipmh.common import Metadata

from oaipmh.server import oai_dc_writer


class FederatedExperimentProvider(DcExperimentProvider):
    """
    Dublin Core provider with identifier and creator fieldsets
    """

    def _get_experiment_metadata(self, experiment, metadataPrefix):
        return Metadata({
            '_writeMetadata': lambda e, m: oai_dc_writer(e, m),
            'title': [experiment.title],
            'description': [experiment.description],
            'identifier': [str(experiment.id)],
            'creator': [str(x.id) for x in experiment.get_owners()]
        })
