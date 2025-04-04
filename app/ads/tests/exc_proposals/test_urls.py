from unittest import TestCase

from django.urls import resolve, reverse


class ExcProposalsUrlsTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.exc_proposals_id = 1

    def test_exc_proposals_detail(self):
        assert (
            reverse('api:exc_proposals-detail', kwargs={'pk': self.exc_proposals_id})
            == f'/api/exc_proposals/{self.exc_proposals_id}/'
        )
        assert (
            resolve(f'/api/exc_proposals/{self.exc_proposals_id}/').view_name
            == 'api:exc_proposals-detail'
        )

    def test_exc_proposals_list(self):
        assert reverse('api:exc_proposals-list') == '/api/exc_proposals/'
        assert resolve('/api/exc_proposals/').view_name == 'api:exc_proposals-list'
