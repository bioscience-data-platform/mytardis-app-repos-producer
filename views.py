from django.http import HttpResponse
import json
from django.contrib.auth.models import User
from tardis.tardis_portal.models import Experiment


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
