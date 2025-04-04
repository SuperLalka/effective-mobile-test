import random
import secrets
from json import dumps
from uuid import uuid4

from django.contrib.auth.models import User
from django.urls import reverse
from faker import Faker
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from app.ads.models import Ad, ExchangeProposal
from app.ads.tests.enums import AdvertsItemConditions
from config import settings

APPLICATION_JSON = 'application/json'

fake = Faker()


class AdAPITestCase(APITestCase):

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
        self.another_user = baker.make(
            User,
            **{
                'username': 'another-tester',
                'email': 'another-tester@test.com',
                'password': secrets.token_hex(16),
            }
        )

        self.client.force_authenticate(self.user)

        self.user_1_ad_1 = baker.make(
            'ads.Ad',
            **{
                'title': fake.text(max_nb_chars=40),
                'category': fake.word(),
                'condition': random.choice(AdvertsItemConditions.values()),
                'user': self.user
            }
        )
        self.user_2_ad_1 = baker.make(
            'ads.Ad',
            **{
                'title': fake.text(max_nb_chars=40),
                'category': fake.word(),
                'condition': random.choice(AdvertsItemConditions.values()),
                'user': self.another_user
            }
        )

        self.exc_proposal = baker.make(
            'ads.ExchangeProposal',
            **{
                'status': ExchangeProposal.StatusChoices.AWAITS,
                'ad_sender': self.user_1_ad_1,
                'ad_receiver': self.user_2_ad_1,
            }
        )

    def test_ads_retrieve(self):
        # УСПЕХ. Запрос от лица пользователя своего объекта Ad
        rsp = self.client.get(reverse('api:ads-detail', args=[self.user_1_ad_1.id]))
        self.assertEqual(rsp.status_code, status.HTTP_200_OK, rsp.data)

        self.assertEqual(rsp.data.get('id'), self.user_1_ad_1.id)
        self.assertIn('title', rsp.data)
        self.assertIn('description', rsp.data)
        self.assertIn('image_url', rsp.data)
        self.assertIn('category', rsp.data)
        self.assertIn('condition', rsp.data)
        self.assertIn('created_at', rsp.data)
        self.assertIn('user', rsp.data)

        # УСПЕХ. Запрос от лица пользователя чужого объекта Ad
        rsp = self.client.get(reverse('api:ads-detail', args=[self.user_2_ad_1.id]))
        self.assertEqual(rsp.status_code, status.HTTP_200_OK, rsp.data)

        # ПРОВАЛ. Запрос от лица анонимного пользователя объекта Ad
        self.client.force_authenticate(None)
        rsp = self.client.get(reverse('api:ads-detail', args=[self.user_2_ad_1.id]))
        self.assertEqual(rsp.status_code, status.HTTP_403_FORBIDDEN)

    def test_ads_list(self):
        baker.make(
            'ads.Ad',
            **{
                'title': fake.text(max_nb_chars=40),
                'category': fake.word(),
                'condition': random.choice(AdvertsItemConditions.values()),
                'user': random.choice([self.user, self.another_user])
            },
            _quantity=settings.REST_FRAMEWORK['PAGE_SIZE'] + 50
        )

        # УСПЕХ. Запрос от лица пользователя списка объектов Ad
        rsp = self.client.get(reverse('api:ads-list'))
        self.assertEqual(rsp.status_code, status.HTTP_200_OK, rsp.data)

        self.assertIn('results', rsp.data)
        self.assertIn('count', rsp.data)
        self.assertTrue(rsp.data['count'], settings.REST_FRAMEWORK['PAGE_SIZE'])
        self.assertIsNotNone(rsp.data.get('next'))

        # ПРОВАЛ. Запрос от лица анонимного пользователя списка объектов Ad
        self.client.force_authenticate(None)
        rsp = self.client.get(reverse('api:ads-list'))
        self.assertEqual(rsp.status_code, status.HTTP_403_FORBIDDEN)

    def test_ads_create(self):
        # УСПЕХ. Создание с корректными данными от лица пользователя
        new_advert_data = {
            'title': str(uuid4()),
            'description': fake.sentence(),
            'image_url': fake.url(),
            'category': fake.word(),
            'condition': random.choice(AdvertsItemConditions.values()),
        }
        rsp = self.client.post(
            reverse('api:ads-list'),
            data=dumps(new_advert_data),
            content_type=APPLICATION_JSON
        )
        self.assertEqual(rsp.status_code, status.HTTP_201_CREATED, rsp.data)

        new_ad = Ad.objects.filter(title=new_advert_data['title']).first()
        self.assertIsNotNone(new_ad)
        [
            self.assertEqual(getattr(new_ad, key), new_advert_data.get(key))
            for key in new_advert_data
        ]

        # ПРОВАЛ. Создание с некорректными данными от лица пользователя
        REQUIRED_FIELDS = ['title', 'category', 'condition']
        for field in REQUIRED_FIELDS:
            new_advert_data_copy = new_advert_data.copy()
            del new_advert_data_copy[field]

            rsp = self.client.post(
                reverse('api:ads-list'),
                data=dumps(new_advert_data_copy),
                content_type=APPLICATION_JSON
            )
            self.assertEqual(rsp.status_code, status.HTTP_400_BAD_REQUEST)

        # ПРОВАЛ. Создание с корректными данными от лица анонимного пользователя
        self.client.force_authenticate(None)
        new_advert_data = {
            'title': str(uuid4()),
            'description': fake.sentence(),
            'image_url': fake.url(),
            'category': fake.word(),
            'condition': random.choice(AdvertsItemConditions.values()),
        }
        rsp = self.client.post(
            reverse('api:ads-list'),
            data=dumps(new_advert_data),
            content_type=APPLICATION_JSON
        )
        self.assertEqual(rsp.status_code, status.HTTP_403_FORBIDDEN)

    def test_ads_update(self):
        update_advert_data = {'title': fake.sentence()}
        rsp = self.client.put(
            reverse('api:ads-detail', args=[self.user_1_ad_1.id]),
            data=dumps(update_advert_data),
            content_type=APPLICATION_JSON
        )
        self.assertEqual(rsp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_ads_partial_update(self):
        # УСПЕХ. Запрос от лица пользователя обновления своего объекта Ad
        update_advert_data = {
            'title': fake.sentence(),
            'description': fake.sentence(),
            'image_url': fake.url(),
            'category': fake.word(),
            'condition': random.choice(AdvertsItemConditions.values()),
        }
        for key, new_value in update_advert_data.items():
            rsp = self.client.patch(
                reverse('api:ads-detail', args=[self.user_1_ad_1.id]),
                data=dumps({key: new_value}),
                content_type=APPLICATION_JSON
            )
            self.assertEqual(rsp.status_code, status.HTTP_200_OK, rsp.data)

            self.user_1_ad_1.refresh_from_db()

            self.assertEqual(getattr(self.user_1_ad_1, key), new_value)

        # ПРОВАЛ. Запрос от лица пользователя обновления чужого объекта Ad
        rsp = self.client.patch(
            reverse('api:ads-detail', args=[self.user_2_ad_1.id]),
            data=dumps({'title': fake.sentence()}),
            content_type=APPLICATION_JSON
        )
        self.assertEqual(rsp.status_code, status.HTTP_403_FORBIDDEN)

        # ПРОВАЛ. Запрос от лица анонимного пользователя обновления объекта Ad
        self.client.force_authenticate(None)
        rsp = self.client.patch(
            reverse('api:ads-detail', args=[self.user_2_ad_1.id]),
            data=dumps({'title': fake.sentence()}),
            content_type=APPLICATION_JSON
        )
        self.assertEqual(rsp.status_code, status.HTTP_403_FORBIDDEN)

    def test_ads_delete(self):
        # УСПЕХ. Запрос от лица пользователя удаления своего объекта Ad
        rsp = self.client.delete(reverse('api:ads-detail', args=[self.user_1_ad_1.id]))
        self.assertEqual(rsp.status_code, status.HTTP_204_NO_CONTENT, rsp.data)

        # ПРОВАЛ. Запрос от лица пользователя удаления чужого объекта Ad
        rsp = self.client.delete(reverse('api:ads-detail', args=[self.user_2_ad_1.id]))
        self.assertEqual(rsp.status_code, status.HTTP_403_FORBIDDEN)

        # ПРОВАЛ. Запрос от лица анонимного пользователя удаления объекта Ad
        self.client.force_authenticate(None)
        rsp = self.client.delete(reverse('api:ads-detail', args=[self.user_2_ad_1.id]))
        self.assertEqual(rsp.status_code, status.HTTP_403_FORBIDDEN)
