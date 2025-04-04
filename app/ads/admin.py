from django.contrib import admin

from app.ads.models import Ad, ExchangeProposal
from app.utils.admin import ExcProposalsReceiveInline, ExcProposalsSendersInline


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            'Object info',
            {'fields': (
                'title',
                'description',
                'image_url',
                'category',
                'condition',
                'created_at',
            )}
        ),
        (
            'Related objects',
            {'fields': ('user',)}
        ),
    )
    list_display = ['id', 'title', 'category', 'condition', 'created_at']
    list_display_links = list_display[:2]
    list_filter = ['category', 'condition']
    raw_id_fields = ['user']
    readonly_fields = ['created_at']
    search_fields = ['title', 'user__id']
    search_help_text = 'Search by title or user_id'

    inlines = [ExcProposalsReceiveInline, ExcProposalsSendersInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('sender_proposals', 'receive_proposals')


@admin.register(ExchangeProposal)
class ExcProposalAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            'Object info',
            {'fields': (
                'comment',
                'status',
                'created_at',
            )}
        ),
        (
            'Related objects',
            {'fields': (
                'ad_sender',
                'ad_receiver',
            )}
        ),
    )
    list_display = ['id', '__str__', 'status', 'created_at']
    list_display_links = list_display[:2]
    list_filter = ['status']
    list_select_related = ['ad_sender', 'ad_receiver']
    raw_id_fields = ['ad_sender', 'ad_receiver']
    readonly_fields = ['created_at']
    search_fields = ['ad_sender__id', 'ad_receiver__id']
    search_help_text = 'Search by ads_id'
