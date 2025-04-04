from rest_framework.routers import DefaultRouter

from app.ads.views.api import ads as ads_views
from app.ads.views.api import exc_proposals as exc_proposals_views

router = DefaultRouter()

router.register('ads', ads_views.AdsViewSet, basename='ads')
router.register('exc_proposals', exc_proposals_views.ExcProposalsViewSet, basename='exc_proposals')


app_name = 'api'
urlpatterns = router.urls
