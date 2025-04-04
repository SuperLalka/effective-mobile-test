
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import permission_classes as view_permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request

from app.ads.filters import ExcProposalsFilter
from app.ads.models import ExchangeProposal
from app.ads.serializers.exc_proposals import (
    ExcProposalSerializer,
    CreateExcProposalSerializer,
    RetrieveExcProposalSerializer,
    UpdateExcProposalSerializer
)
from app.utils.permissions import UserIsObjectOwner
from app.utils.mixins import PermissionsPerMethodMixin


class ExcProposalsViewSet(PermissionsPerMethodMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = ExchangeProposal.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ExcProposalSerializer
    filterset_class = ExcProposalsFilter

    action_serializers = {
        'list': RetrieveExcProposalSerializer,
        'create': CreateExcProposalSerializer,
        'retrieve': RetrieveExcProposalSerializer,
        'partial_update': UpdateExcProposalSerializer,
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

        serializer = self.get_serializer_class()(data=request_data, context={'request': request})
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
