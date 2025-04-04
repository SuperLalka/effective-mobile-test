
from django_filters import rest_framework as filters

from app.ads.models import Ad, ExchangeProposal


class AdsFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')
    category = filters.CharFilter(lookup_expr='icontains')
    condition = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Ad
        fields = ['title', 'description', 'category', 'condition']


class ExcProposalsFilter(filters.FilterSet):
    ad_sender = filters.CharFilter(lookup_expr='icontains')
    ad_receiver = filters.CharFilter(lookup_expr='icontains')
    status = filters.ChoiceFilter(choices=ExchangeProposal.StatusChoices.choices)

    class Meta:
        model = ExchangeProposal
        fields = ['ad_sender', 'ad_receiver', 'status']
