
from django_admin_inline_paginator.admin import TabularInlinePaginated

from app.ads.models import ExchangeProposal


class ExcProposalsInlineBase(TabularInlinePaginated):
    model = ExchangeProposal
    fields = ('created_at', 'status', 'ad_sender', 'ad_receiver')
    readonly_fields = ['created_at']
    ordering = ['created_at']
    per_page = 100
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ExcProposalsSendersInline(ExcProposalsInlineBase):
    fk_name = 'ad_sender'
    verbose_name = 'Исходящее предложение'
    verbose_name_plural = 'Исходящие предложения'


class ExcProposalsReceiveInline(ExcProposalsInlineBase):
    fk_name = 'ad_receiver'
    verbose_name = 'Входящее предложение'
    verbose_name_plural = 'Входящие предложения'
