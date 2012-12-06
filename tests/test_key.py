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

from tardis.tardis_portal.models import ExperimentParameter, \
    ExperimentParameterSet, ParameterName, Schema

from django.conf import settings

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

    license_ = License(name='Creative Commons Attribution-'
        + 'NoDerivs 2.5 Australia',
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

    sch, _ = Schema.objects.get_or_create(namespace=settings.KEY_NAMESPACE,
                                          name=settings.KEY_NAME,
                                          type=Schema.EXPERIMENT)

    pn, _ = ParameterName.objects.\
            get_or_create(schema=sch, name=settings.KEY_NAME,
                data_type=ParameterName.STRING)


    return experiment


class DOITest(TestCase):

    def setUp(self):
        pass

    def test_mint(self):
        import json
        client = Client()
        experiment = _create_test_data()
        response = client.get('/apps/reposproducer/key/%s/'
            % experiment.id,
            follow=True)

        response_obj = json.loads(response.content)
        self.assertTrue(response_obj)


        response = client.get('/apps/reposproducer/key/%s/'
            % experiment.id,
            follow=True)
        new_response_obj = json.loads(response.content)
        self.assertEquals(new_response_obj, response_obj)

