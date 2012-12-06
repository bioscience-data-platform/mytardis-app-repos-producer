import random
import json
import logging
import string

from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.models import User
from tardis.tardis_portal.models import Experiment
from tardis.tardis_portal.models import ExperimentParameter, \
    ExperimentParameterSet, ParameterName, Schema
from tardis.tardis_portal.shortcuts import render_response_index, \
    return_response_error, return_response_not_found, \
    render_response_search, render_error_message, \
    get_experiment_referer

logger = logging.getLogger(__name__)


def user(request, user_id):
    """
    Return json for a specified user profile
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponse('User profile %s does not exist' % user_id)
    obj = {}
    obj['id'] = user.id
    obj['first_name'] = user.first_name
    obj['last_name'] = user.last_name
    obj['username'] = user.username
    obj['email'] = user.email

    return HttpResponse(json.dumps(obj), mimetype='application/json')


def experiment_state(request, exp_id):

    try:
        experiment = Experiment.objects.get(id=exp_id)
    except Experiment.DoesNotExist:
        return HttpResponse('Experiment does not exist')

    return HttpResponse(json.dumps(experiment.public_access),
        mimetype='application/json')


def get_acls(request, exp_id):

    try:
        experiment = Experiment.objects.get(id=exp_id)
    except Experiment.DoesNotExist:
        return HttpResponse('Experiment does not exist')

    if experiment.public_access in [Experiment.PUBLIC_ACCESS_FULL,
                              Experiment.PUBLIC_ACCESS_METADATA]:
        # TODO: only send user owner-like acls for now, because difficult
        # to reconcile rest on destination which may have different existing
        # users groups etc.

        acls = []
        for user_acl in Experiment.safe.user_acls(request, experiment.id):
            acl = {}
            for key in ['id', 'pluginId', 'entityId', 'isOwner',
                        'canRead', 'canWrite', 'canDelete',
                        #'effectiveDate', 'expiryDate', #TODO: build json serialiser for this
                        'aclOwnershipType']:
                try:
                    acl[key] = getattr(user_acl, key)
                except ValueError:
                    return HttpResponse("Cannot read ACLs")
            acls.append(acl)
    else:
        return HttpResponse('No Information Available')

    return HttpResponse(json.dumps(acls),
        mimetype='application/json')


class ExperimentKeyService(object):

    def __init__(self):
        self.schema = Schema.objects.get(namespace=settings.KEY_NAMESPACE)
        self.key_name = ParameterName.objects.get(name=settings.KEY_NAME)

    def get_key(self, experiment):
        """
        """
        doi_params = ExperimentParameter.objects.filter(
            name=self.key_name,
            parameterset__schema=self.schema,
            parameterset__experiment=experiment)
        if doi_params.count() == 1:
            return doi_params[0].string_value
        return None

    def _make_rand_string(self, number_of_chars):
        """
        """
        return ''.join(random.choice(string.ascii_uppercase
            + string.ascii_lowercase + string.digits)
            for x in range(number_of_chars))

    def mint_key(self, experiment):
        number_chars = 64
        key_value = self._make_rand_string(number_chars)
        eps, _ = ExperimentParameterSet.objects.\
            get_or_create(experiment=experiment, schema=self.schema)
        ep = ExperimentParameter(parameterset=eps,
            name=self.key_name,
            string_value=key_value)
        ep.save()
        return key_value


def mint_key(request, exp_id):

    experiment = Experiment.objects.get(id=exp_id)

    try:
        key_service = ExperimentKeyService()
    except Schema.DoesNotExist:
        logger.exception("No ExperimentKeyService Schema found")
        return return_response_error(request)
    except ParameterName.DoesNotExist:
        logger.exception("No ExperimentKeyService ParameterName found")
        return return_response_error(request)

    key = key_service.get_key(experiment)
    if not key:
        key = key_service.mint_key(experiment)

    return HttpResponse(json.dumps(key),
        mimetype='application/json')
