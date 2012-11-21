from tardis.apps.oaipmh.provider.experiment import DcExperimentProvider
from tardis.tardis_portal.models import Author_Experiment, Experiment,\
    ExperimentParameterSet, License, User
from oaipmh.common import Identify, Header, Metadata
import oaipmh.error
from oaipmh.interfaces import IOAI
from oaipmh.metadata import global_metadata_registry
from oaipmh.server import Server, oai_dc_writer, NS_XSI

class FederatedExperimentProvider(DcExperimentProvider):
   
    def _get_experiment_metadata(self, experiment, metadataPrefix):
        return Metadata({
            '_writeMetadata': lambda e, m: oai_dc_writer(e, m),
            'title': [experiment.title],
            'description': [experiment.description],
            'identifier': [str(experiment.id)]
        })