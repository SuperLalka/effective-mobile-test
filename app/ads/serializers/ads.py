
from django.contrib.auth.models import User
from rest_framework import serializers

from app.ads.models import Ad


class AdSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ad
        fields = '__all__'


class CreateAdSerializer(AdSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())


class RetrieveAdSerializer(AdSerializer):
    pass


class UpdateAdSerializer(AdSerializer):
    pass

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.image_url = validated_data.get('image_url', instance.image_url)
        instance.category = validated_data.get('category', instance.category)
        instance.condition = validated_data.get('condition', instance.condition)
        instance.save()
        return instance
