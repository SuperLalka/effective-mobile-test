
from rest_framework import serializers

from app.ads.models import ExchangeProposal, Ad


class ExcProposalSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExchangeProposal
        fields = '__all__'


class CreateExcProposalSerializer(ExcProposalSerializer):
    ad_sender = serializers.PrimaryKeyRelatedField(
        queryset=Ad.objects.all()
    )
    ad_receiver = serializers.PrimaryKeyRelatedField(
        queryset=Ad.objects.all()
    )

    def validate(self, attrs):
        request = self.context['request']

        if attrs['ad_sender'].user != request.user:
            raise serializers.ValidationError(
                "It is prohibited to offer other people's ads for exchange."
            )

        if (ExchangeProposal.objects
                .filter(
                    ad_sender=attrs['ad_sender'],
                    ad_receiver=attrs['ad_receiver'],
                    status=ExchangeProposal.StatusChoices.AWAITS,
                )
                .exists()
        ):
            raise serializers.ValidationError('A similar proposal in pending status already exists.')
        return attrs


class RetrieveExcProposalSerializer(ExcProposalSerializer):
    pass


class UpdateExcProposalSerializer(ExcProposalSerializer):
    pass

    def validate_status(self, value: str) -> str:
        if value not in ExchangeProposal.StatusChoices.values:
            raise serializers.ValidationError(f"Valid values: {ExchangeProposal.StatusChoices.values}")
        return value

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance
