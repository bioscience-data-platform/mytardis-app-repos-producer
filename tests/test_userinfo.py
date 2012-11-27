# -*- coding: utf-8 -*-
#
# Copyright (c) 2012, RMIT eResearch Office
#   (RMIT University, Australia)
# Copyright (c) 2010-2012, Monash e-Research Centre
#   (Monash University, Australia)
# Copyright (c) 2010-2011, VeRSI Consortium
#   (Victorian eResearch Strategic Initiative, Australia)
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    *  Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#    *  Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#    *  Neither the name of the VeRSI, the VeRSI Consortium members, nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE REGENTS AND CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#


import logging
logger = logging.getLogger(__name__)

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

from lxml import etree

from tardis.tardis_portal.models import \
    Experiment, ExperimentACL, License, UserProfile

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


def _create_test_data():
    """
    Create Single experiment with two owners
    """
    user1 = User(username='tom',
                first_name='Thomas',
                last_name='Atkins',
                email='tommy@atkins.net')
    user1.save()
    UserProfile(user=user1).save()

    user2 = User(username='joe',
                first_name='Joe',
                last_name='Bloggs',
                email='joe@mail.com')
    user2.save()
    UserProfile(user=user2).save()

    license_ = License(name='Creative Commons Attribution-NoDerivs 2.5 Australia',
                       url='http://creativecommons.org/licenses/by-nd/2.5/au/',
                       internal_description='CC BY 2.5 AU',
                       allows_distribution=True)
    license_.save()
    experiment = Experiment(title='Norwegian Blue',
                            description='Parrot + 40kV',
                            created_by=user1)
    experiment.public_access = Experiment.PUBLIC_ACCESS_FULL
    experiment.license = license_
    experiment.save()
    experiment.author_experiment_set.create(order=0,
                                            author="John Cleese",
                                            url="http://nla.gov.au/nla.party-1")
    experiment.author_experiment_set.create(order=1,
                                            author="Michael Palin",
                                            url="http://nla.gov.au/nla.party-2")

    acl1 = ExperimentACL(experiment=experiment,
                    pluginId='django_user',
                    entityId=str(user1.id),
                    isOwner=True,
                    canRead=True,
                    canWrite=True,
                    canDelete=True,
                    aclOwnershipType=ExperimentACL.OWNER_OWNED)
    acl1.save()

    acl2 = ExperimentACL(experiment=experiment,
                    pluginId='django_user',
                    entityId=str(user2.id),
                    isOwner=True,
                    canRead=True,
                    canWrite=True,
                    canDelete=True,
                    aclOwnershipType=ExperimentACL.OWNER_OWNED)
    acl2.save()
    return experiment


class ExpStateTest(TestCase):
    """ Retrieving state of an experiment
    """

    def setUp(self):
        self._client = Client()
        self.exp = _create_test_data()

    def testGetRecord(self):
        """
        Retrieve information about a user
        """
        import json
        response = self._client_get('/apps/reposproducer/expstate/%s/'
            % self.exp.id,
            follow=True)
        response_obj = json.loads(response.content)
        self.assertEqual(response_obj, Experiment.PUBLIC_ACCESS_FULL)

        self.exp.public_access = Experiment.PUBLIC_ACCESS_METADATA
        self.exp.save()
        response = self._client_get('/apps/reposproducer/expstate/%s/'
            % self.exp.id,
            follow=True)
        response_obj = json.loads(response.content)
        self.assertEqual(response_obj, Experiment.PUBLIC_ACCESS_METADATA)

        self.exp.public_access = Experiment.PUBLIC_ACCESS_NONE
        self.exp.save()
        response = self._client_get('/apps/reposproducer/expstate/%s/'
            % self.exp.id,
            follow=True)
        response_obj = json.loads(response.content)
        self.assertEqual(response_obj, Experiment.PUBLIC_ACCESS_NONE)

    def _client_get(self, url, **kwargs):
        return self._client.get(url, kwargs)


class GetACLTest(TestCase):
    """ Retrieving the ACLS for an experiment
    """

    def setUp(self):
        self._client = Client()
        self.exp = _create_test_data()

    def testGetRecord(self):
        """
        Retrieve information about a user
        """
        import json
        response = self._client_get('/apps/reposproducer/acls/%s/'
            % self.exp.id,
            follow=True)
        response_obj = json.loads(response.content)
        self.assertEqual(sorted([x['id'] for x in response_obj]), [1, 2])
        self.assertEqual(sorted([x['canDelete'] for x in response_obj]),
            [True, True])
        self.assertEqual(sorted([x['canRead'] for x in response_obj]),
            [True, True])
        self.assertEqual(sorted([x['canWrite'] for x in response_obj]),
             [True, True])
        self.assertEqual(sorted([x['isOwner'] for x in response_obj]),
             [True, True])
        self.assertEqual(sorted([x['entityId'] for x in response_obj]),
             ['1', '2'])

    def _client_get(self, url, **kwargs):
        return self._client.get(url, kwargs)
