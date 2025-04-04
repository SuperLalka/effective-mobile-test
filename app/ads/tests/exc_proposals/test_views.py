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

from app.ads.models import ExchangeProposal
from app.ads.tests.enums import AdvertsItemConditions
from config import settings

APPLICATION_JSON = 'application/json'

fake = Faker()


class ExcProposalAPITestCase(APITestCase):

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
        self.user_1_ad_2 = baker.make(
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
        self.user_2_ad_2 = baker.make(
            'ads.Ad',
            **{
                'title': fake.text(max_nb_chars=40),
                'category': fake.word(),
                'condition': random.choice(AdvertsItemConditions.values()),
                'user': self.another_user
            }
        )

        self.exc_proposal_1 = baker.make(
            'ads.ExchangeProposal',
            **{
                'status': ExchangeProposal.StatusChoices.AWAITS,
                'ad_sender': self.user_1_ad_1,
                'ad_receiver': self.user_2_ad_1,
            }
        )
        self.exc_proposal_2 = baker.make(
            'ads.ExchangeProposal',
            **{
                'status': ExchangeProposal.StatusChoices.AWAITS,
                'ad_sender': self.user_2_ad_1,
                'ad_receiver': self.user_1_ad_1,
            }
        )

    def test_exc_proposals_retrieve(self):
        # УСПЕХ. Запрос от лица пользователя объекта ExchangeProposal в котором он SENDER
        rsp = self.client.get(reverse('api:exc_proposals-detail', args=[self.exc_proposal_1.id]))
        self.assertEqual(rsp.status_code, status.HTTP_200_OK, rsp.data)

        self.assertEqual(rsp.data.get('id'), self.exc_proposal_1.id)
        self.assertIn('comment', rsp.data)
        self.assertIn('status', rsp.data)
        self.assertIn('created_at', rsp.data)
        self.assertIn('ad_sender', rsp.data)
        self.assertIn('ad_receiver', rsp.data)

        # УСПЕХ. Запрос от лица пользователя объекта ExchangeProposal в котором он RECEIVER
        rsp = self.client.get(reverse('api:exc_proposals-detail', args=[self.exc_proposal_2.id]))
        self.assertEqual(rsp.status_code, status.HTTP_200_OK, rsp.data)

        # ПРОВАЛ. Запрос от лица анонимного пользователя объекта ExchangeProposal
        self.client.force_authenticate(None)
        rsp = self.client.get(reverse('api:exc_proposals-detail', args=[self.exc_proposal_2.id]))
        self.assertEqual(rsp.status_code, status.HTTP_403_FORBIDDEN)

    def test_exc_proposals_list(self):
        baker.make(
            'ads.ExchangeProposal',
            **{
                'status': random.choice(ExchangeProposal.StatusChoices.values),
                'ad_sender': baker.make(
                    'ads.Ad',
                    **{
                        'title': fake.text(max_nb_chars=40),
                        'category': fake.word(),
                        'condition': random.choice(AdvertsItemConditions.values()),
                        'user': self.user
                    }
                ),
                'ad_receiver': baker.make(
                    'ads.Ad',
                    **{
                        'title': fake.text(max_nb_chars=40),
                        'category': fake.word(),
                        'condition': random.choice(AdvertsItemConditions.values()),
                        'user': self.another_user
                    }
                ),
            },
            _quantity=settings.REST_FRAMEWORK['PAGE_SIZE'] + 50
        )

        # УСПЕХ. Запрос от лица пользователя списка объектов ExchangeProposal
        rsp = self.client.get(reverse('api:exc_proposals-list'))
        self.assertEqual(rsp.status_code, status.HTTP_200_OK, rsp.data)

        self.assertIn('results', rsp.data)
        self.assertIn('count', rsp.data)
        self.assertTrue(rsp.data['count'], settings.REST_FRAMEWORK['PAGE_SIZE'])
        self.assertIsNotNone(rsp.data.get('next'))

        # ПРОВАЛ. Запрос от лица анонимного пользователя списка объектов ExchangeProposal
        self.client.force_authenticate(None)
        rsp = self.client.get(reverse('api:exc_proposals-list'))
        self.assertEqual(rsp.status_code, status.HTTP_403_FORBIDDEN)

    def test_exc_proposals_create(self):
        # УСПЕХ. Создание с корректными данными от лица пользователя
        new_proposals_data = {
            'comment': str(uuid4()),
            'ad_sender': self.user_1_ad_2.id,
            'ad_receiver': self.user_2_ad_2.id,
        }
        rsp = self.client.post(
            reverse('api:exc_proposals-list'),
            data=dumps(new_proposals_data),
            content_type=APPLICATION_JSON
        )
        self.assertEqual(rsp.status_code, status.HTTP_201_CREATED, rsp.data)

        new_proposal = ExchangeProposal.objects.filter(comment=new_proposals_data['comment']).first()
        self.assertIsNotNone(new_proposal)
        self.assertEqual(new_proposal.ad_sender.id, new_proposals_data['ad_sender'])
        self.assertEqual(new_proposal.ad_receiver.id, new_proposals_data['ad_receiver'])

        # ПРОВАЛ. Создание с корректными данными от лица пользователя,
        # но объект с указанными ключами ad_sender, ad_receiver и status = AWAITS уже существует
        rsp = self.client.post(
            reverse('api:exc_proposals-list'),
            data=dumps(new_proposals_data),
            content_type=APPLICATION_JSON
        )

        self.assertEqual(rsp.status_code, status.HTTP_400_BAD_REQUEST)

        # ПРОВАЛ. Создание с некорректными данными от лица пользователя
        # (указание чужого объекта ExchangeProposal в роли SENDER'а)
        new_proposals_data = {
            'comment': str(uuid4()),
            'ad_sender': self.user_2_ad_2.id,
            'ad_receiver': self.user_1_ad_2.id,
        }
        rsp = self.client.post(
            reverse('api:exc_proposals-list'),
            data=dumps(new_proposals_data),
            content_type=APPLICATION_JSON
        )
        self.assertEqual(rsp.status_code, status.HTTP_400_BAD_REQUEST)

        # ПРОВАЛ. Создание с корректными данными от лица анонимного пользователя
        self.client.force_authenticate(None)
        rsp = self.client.post(
            reverse('api:exc_proposals-list'),
            data=dumps(new_proposals_data),
            content_type=APPLICATION_JSON
        )
        self.assertEqual(rsp.status_code, status.HTTP_403_FORBIDDEN)

    def test_exc_proposals_update(self):
        update_proposals_data = {'status': random.choice(ExchangeProposal.StatusChoices.values)}
        rsp = self.client.put(
            reverse('api:exc_proposals-detail', args=[self.exc_proposal_1.id]),
            data=dumps(update_proposals_data),
            content_type=APPLICATION_JSON
        )
        self.assertEqual(rsp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_exc_proposals_partial_update(self):
        # УСПЕХ. Запрос от лица пользователя обновления своего объекта ExchangeProposal
        update_proposals_data = {'status': random.choice(ExchangeProposal.StatusChoices.values)}
        rsp = self.client.patch(
            reverse('api:exc_proposals-detail', args=[self.exc_proposal_1.id]),
            data=dumps(update_proposals_data),
            content_type=APPLICATION_JSON
        )
        self.assertEqual(rsp.status_code, status.HTTP_200_OK, rsp.data)

        self.exc_proposal_1.refresh_from_db()

        self.assertEqual(self.exc_proposal_1.status, update_proposals_data['status'])

        # ПРОВАЛ. Запрос от лица пользователя обновления чужого объекта ExchangeProposal
        rsp = self.client.patch(
            reverse('api:exc_proposals-detail', args=[self.exc_proposal_2.id]),
            data=dumps(update_proposals_data),
            content_type=APPLICATION_JSON
        )
        self.assertEqual(rsp.status_code, status.HTTP_403_FORBIDDEN)

        # ПРОВАЛ. Запрос от лица анонимного пользователя обновления объекта ExchangeProposal
        self.client.force_authenticate(None)
        rsp = self.client.patch(
            reverse('api:exc_proposals-detail', args=[self.exc_proposal_2.id]),
            data=dumps(update_proposals_data),
            content_type=APPLICATION_JSON
        )
        self.assertEqual(rsp.status_code, status.HTTP_403_FORBIDDEN)

    def test_exc_proposals_delete(self):
        # УСПЕХ. Запрос от лица пользователя удаления своего объекта ExchangeProposal
        rsp = self.client.delete(reverse('api:exc_proposals-detail', args=[self.exc_proposal_1.id]))
        self.assertEqual(rsp.status_code, status.HTTP_204_NO_CONTENT, rsp.data)

        # ПРОВАЛ. Запрос от лица пользователя удаления чужого объекта ExchangeProposal
        rsp = self.client.delete(reverse('api:exc_proposals-detail', args=[self.exc_proposal_2.id]))
        self.assertEqual(rsp.status_code, status.HTTP_403_FORBIDDEN)

        # ПРОВАЛ. Запрос от лица анонимного пользователя удаления объекта ExchangeProposal
        self.client.force_authenticate(None)
        rsp = self.client.delete(reverse('api:exc_proposals-detail', args=[self.exc_proposal_2.id]))
        self.assertEqual(rsp.status_code, status.HTTP_403_FORBIDDEN)
