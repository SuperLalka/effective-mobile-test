
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import permission_classes as view_permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request

from app.ads.filters import AdsFilter
from app.ads.models import Ad
from app.ads.serializers.ads import (
    AdSerializer,
    CreateAdSerializer,
    RetrieveAdSerializer,
    UpdateAdSerializer
)
from app.utils.permissions import UserIsObjectOwner
from app.utils.mixins import PermissionsPerMethodMixin


class AdsViewSet(PermissionsPerMethodMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Ad.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = AdSerializer
    filterset_class = AdsFilter

    action_serializers = {
        'list': RetrieveAdSerializer,
        'create': CreateAdSerializer,
        'retrieve': RetrieveAdSerializer,
        'partial_update': UpdateAdSerializer,
    }

    def get_serializer_class(self):
        return self.action_serializers.get(self.action, self.serializer_class)

    def list(self, request: Request, *args, **kwargs) -> Response:
        return super().list(self, request, *args, **kwargs)

    def retrieve(self, request: Request, pk: int = None) -> Response:
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        response_data = self.get_serializer_class()(instance).data
        return Response(response_data, status=status.HTTP_200_OK)

    def create(self, request: Request) -> Response:
        request_data = request.data.copy()
        request_data['user'] = request.user.id

        serializer = self.get_serializer_class()(data=request_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request: Request, pk: int = None) -> Response:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @view_permission_classes([UserIsObjectOwner])
    def partial_update(self, request: Request, pk: int = None) -> Response:
        instance = get_object_or_404(self.get_queryset(), id=pk)
        serializer = self.get_serializer_class()(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @view_permission_classes([UserIsObjectOwner])
    def destroy(self, request: Request, pk: int = None) -> Response:
        instance = get_object_or_404(self.get_queryset(), id=pk)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
