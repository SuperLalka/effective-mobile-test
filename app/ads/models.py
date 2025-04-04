
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


class Ad(models.Model):
    title = models.CharField(max_length=70)
    description = models.TextField(max_length=1000, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=50)
    condition = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='ads',
    )

    OWNER_FIELD = 'user.id'

    class Meta:
        db_table = 'ads'
        verbose_name = 'ADS'
        verbose_name_plural = 'ADSs'

    def __str__(self):
        return f"{self.title} / {self.user}"


class ExchangeProposal(models.Model):
    class StatusChoices(models.TextChoices):
        AWAITS = 'ожидает'
        ACCEPTED = 'принята'
        REJECTED = 'отклонена'

    comment = models.TextField(max_length=500, blank=True, null=True)
    status = models.CharField(
        max_length=9,
        choices=StatusChoices.choices,
        default=StatusChoices.AWAITS
    )

    created_at = models.DateTimeField(auto_now_add=True)

    ad_sender = models.ForeignKey(
        'Ad',
        on_delete=models.CASCADE,
        related_name='sender_proposals',
    )
    ad_receiver = models.ForeignKey(
        'Ad',
        on_delete=models.CASCADE,
        related_name='receive_proposals',
    )

    OWNER_FIELD = 'ad_sender.user.id'

    class Meta:
        db_table = 'exchange_proposal'
        verbose_name = 'Exchange Proposal'
        verbose_name_plural = 'Exchange Proposals'

    def __str__(self):
        return f"#{self.id}: from {self.ad_sender} / to {self.ad_receiver}"

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(ExchangeProposal, self).save(*args, **kwargs)

    def clean(self):
        super(ExchangeProposal, self).clean()
        if (ExchangeProposal.objects
                .filter(
                    ad_sender=self.ad_sender_id,
                    ad_receiver=self.ad_receiver_id,
                    status=self.StatusChoices.AWAITS
                )
                .exclude(id=self.id)
                .exists()
        ):
            raise ValidationError("A similar proposal in pending status already exists.")
