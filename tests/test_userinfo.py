from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client


class UserProfileRetrieveTest(TestCase):
    """ Retrieving user profile information
    """

    def _create_data(self):
        user = User.objects.create_user('testuser',
            'testuser@mail.com',
            'password')
        user.last_name = "User"
        user.first_name = "Test"
        user.save()
        self.user_id = user.id

    def setUp(self):
        self._client = Client()
        self._create_data()

    def testGetRecord(self):
        """
        Retrieve information about a user
        """
        self.assertEquals(self.user_id, 1)
        response = self._client_get('/apps/reposproducer/user/%s/'
            % self.user_id,
            follow=True)
        import json
        response_obj = json.loads(response.content)
        self.assertEqual(response_obj['first_name'], 'Test')
        self.assertEqual(response_obj['last_name'], 'User')
        self.assertEqual(response_obj['email'], 'testuser@mail.com')

    def _client_get(self, url, **kwargs):
        return self._client.get(url, kwargs)
