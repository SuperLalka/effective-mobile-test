import random
import secrets

from django.contrib.auth.models import User
from django.urls import reverse
from faker import Faker
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from app.ads.models import Ad
from app.ads.tests.enums import (
    AD_CATEGORY_EXAMPLES,
    AD_CONDITION_EXAMPLES,
    AD_DESC_KEYWORD_EXAMPLES,
    AD_TITLE_EXAMPLES
)

APPLICATION_JSON = 'application/json'

fake = Faker()


class AdFiltersTestCase(APITestCase):

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

        [
            baker.make(
                'ads.Ad',
                **{
                    'title': self.prepare_string_with_keyword(keys_seq=AD_TITLE_EXAMPLES),
                    'description': self.prepare_string_with_keyword(keys_seq=AD_DESC_KEYWORD_EXAMPLES),
                    'category': random.choice(AD_CATEGORY_EXAMPLES),
                    'condition': random.choice(AD_CONDITION_EXAMPLES),
                    'user': self.user
                }
            ) for _ in range(50)
        ]

    @staticmethod
    def prepare_string_with_keyword(keys_seq: list, words_num: int = 5) -> str:
        words = fake.words(nb=words_num)
        replaced_index = random.randrange(0, words_num)
        words[replaced_index] = random.choice(keys_seq).lower()
        return ' '.join(words)

    def test_filter_by_title(self):
        for title in AD_TITLE_EXAMPLES:
            rsp = self.client.get(reverse('api:ads-list'), data={'title': title})
            self.assertEqual(rsp.status_code, status.HTTP_200_OK, rsp.data)

            self.assertEqual(
                rsp.data['count'],
                Ad.objects.filter(title__icontains=title).count()
            )

    def test_filter_by_description(self):
        for description in AD_DESC_KEYWORD_EXAMPLES:
            rsp = self.client.get(reverse('api:ads-list'), data={'description': description})
            self.assertEqual(rsp.status_code, status.HTTP_200_OK, rsp.data)

            self.assertEqual(
                rsp.data['count'],
                Ad.objects.filter(description__icontains=description).count()
            )

    def test_filter_by_category(self):
        for category in AD_CATEGORY_EXAMPLES:
            rsp = self.client.get(reverse('api:ads-list'), data={'category': category})
            self.assertEqual(rsp.status_code, status.HTTP_200_OK, rsp.data)

            self.assertEqual(
                rsp.data['count'],
                Ad.objects.filter(category__icontains=category).count()
            )

    def test_filter_by_condition(self):
        for condition in AD_CONDITION_EXAMPLES:
            rsp = self.client.get(reverse('api:ads-list'), data={'condition': condition})
            self.assertEqual(rsp.status_code, status.HTTP_200_OK, rsp.data)

            self.assertEqual(
                rsp.data['count'],
                Ad.objects.filter(condition__icontains=condition).count()
            )

    def test_multiple_filter(self):
        for _ in range(5):
            title = random.choice(AD_TITLE_EXAMPLES)
            description = random.choice(AD_DESC_KEYWORD_EXAMPLES)
            category = random.choice(AD_CATEGORY_EXAMPLES)
            condition = random.choice(AD_CONDITION_EXAMPLES)

            rsp = self.client.get(
                reverse('api:ads-list'),
                data={
                    'title': title,
                    'description': description,
                    'category': category,
                    'condition': condition,
                }
            )
            self.assertEqual(rsp.status_code, status.HTTP_200_OK, rsp.data)

            self.assertEqual(
                rsp.data['count'],
                Ad.objects.filter(
                    title__icontains=title,
                    description__icontains=description,
                    category__icontains=category,
                    condition__icontains=condition,
                ).count()
            )
