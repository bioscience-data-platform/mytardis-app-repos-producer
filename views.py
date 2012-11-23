from django.http import HttpResponse
import json
from django.contrib.auth.models import User


def user(request, user_id):
    """
    Return json for a specified user profile
    """
    #FIXME: currently public access
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponse('User profile %s does not exist' % user_id)
    obj = {}
    obj['id'] = user.id
    obj['first_name'] = user.first_name
    obj['last_name'] = user.last_name
    obj['email'] = user.email

    return HttpResponse(json.dumps(obj), mimetype='application/json')
