import random
import secrets

from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse
from faker import Faker
from model_bakery import baker
from rest_framework import status as http_status
from rest_framework.test import APITestCase

from app.ads.models import Ad, ExchangeProposal
from app.ads.tests.enums import (
    AD_CATEGORY_EXAMPLES,
    AD_CONDITION_EXAMPLES,
    AD_DESC_KEYWORD_EXAMPLES,
    AD_TITLE_EXAMPLES
)

APPLICATION_JSON = 'application/json'

fake = Faker()


class ExcProposalsFiltersTestCase(APITestCase):

    def setUp(self) -> None:
        super().setUp()

        self.user = baker.make(
            User,
            **{
                'username': 'tester',
                'email': 'tester@test.com',
                'password': secrets.token_hex(16),
            }
        )

        self.client.force_authenticate(self.user)

        self.users = [
            baker.make(
                User,
                **{
                    'username': fake.name(),
                    'email': fake.email(),
                    'password': secrets.token_hex(16),
                }
            ) for _ in range(10)
        ]

        self.ads = [
            baker.make(
                'ads.Ad',
                **{
                    'title': self.prepare_string_with_keyword(keys_seq=AD_TITLE_EXAMPLES),
                    'description': self.prepare_string_with_keyword(keys_seq=AD_DESC_KEYWORD_EXAMPLES),
                    'category': random.choice(AD_CATEGORY_EXAMPLES),
                    'condition': random.choice(AD_CONDITION_EXAMPLES),
                    'user': user
                }
            ) for _ in range(5) for user in self.users
        ]

        [
            baker.make(
                'ads.ExchangeProposal',
                **{
                    'status': random.choice(ExchangeProposal.StatusChoices.values),
                    'ad_sender': Ad.objects.filter(user=user, sender_proposals__isnull=True).first(),
                    'ad_receiver': Ad.objects.filter(~Q(user=user)).first(),
                }
            ) for _ in range(3) for user in self.users
        ]

    @staticmethod
    def prepare_string_with_keyword(keys_seq: list, words_num: int = 5) -> str:
        words = fake.words(nb=words_num)
        replaced_index = random.randrange(0, words_num)
        words[replaced_index] = random.choice(keys_seq).lower()
        return ' '.join(words)

    def test_filter_by_ad_sender(self):
        for sender in ExchangeProposal.objects.raw(
                'SELECT ad_sender_id as id FROM exchange_proposal GROUP BY ad_sender_id'
        ):
            sender = sender.id
            rsp = self.client.get(reverse('api:exc_proposals-list'), data={'ad_sender': sender})
            self.assertEqual(rsp.status_code, http_status.HTTP_200_OK, rsp.data)

            self.assertEqual(
                rsp.data['count'],
                ExchangeProposal.objects.filter(ad_sender=sender).count()
            )

    def test_filter_by_ad_receiver(self):
        for receiver in ExchangeProposal.objects.raw(
                'SELECT ad_receiver_id as id FROM exchange_proposal GROUP BY ad_receiver_id'
        ):
            receiver = receiver.id
            rsp = self.client.get(reverse('api:exc_proposals-list'), data={'ad_receiver': receiver})
            self.assertEqual(rsp.status_code, http_status.HTTP_200_OK, rsp.data)

            self.assertEqual(
                rsp.data['count'],
                ExchangeProposal.objects.filter(ad_receiver=receiver).count()
            )

    def test_filter_by_status(self):
        for status in ExchangeProposal.StatusChoices.values:
            rsp = self.client.get(reverse('api:exc_proposals-list'), data={'status': status})
            self.assertEqual(rsp.status_code, http_status.HTTP_200_OK, rsp.data)

            self.assertEqual(
                rsp.data['count'],
                ExchangeProposal.objects.filter(status=status).count()
            )

    def test_multiple_filter(self):
        for _ in range(5):
            status = random.choice(ExchangeProposal.StatusChoices.values)
            ad_sender = random.choice(self.ads).id
            ad_receiver = random.choice(self.ads).id

            rsp = self.client.get(
                reverse('api:exc_proposals-list'),
                data={
                    'status': status,
                    'ad_sender': ad_sender,
                    'ad_receiver': ad_receiver,
                }
            )
            self.assertEqual(rsp.status_code, http_status.HTTP_200_OK, rsp.data)

            self.assertEqual(
                rsp.data['count'],
                ExchangeProposal.objects.filter(
                    status=status,
                    ad_sender_id=ad_sender,
                    ad_receiver_id=ad_receiver,
                ).count()
            )
