from unittest import TestCase

from django.urls import resolve, reverse


class AdsUrlsTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.ad_id = 1

    def test_ads_detail(self):
        assert (reverse('api:ads-detail', kwargs={'pk': self.ad_id}) == f'/api/ads/{self.ad_id}/')
        assert resolve(f'/api/ads/{self.ad_id}/').view_name == 'api:ads-detail'

    def test_ads_list(self):
        assert reverse('api:ads-list') == '/api/ads/'
        assert resolve('/api/ads/').view_name == 'api:ads-list'
