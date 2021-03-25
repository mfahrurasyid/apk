import logging
import os
from django.views.generic import View
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .serializers import *
from .models import *



class ReactAppView(View):
    """
    Serves the compiled frontend entry point (only works if you have run `yarn run build`).
    """

    def get(self, request):
        """ GET React view. """
        try:
            with open(os.path.join(settings.REACT_APP_DIR, 'build', 'index.html')) as f:
                return HttpResponse(f.read())
        except FileNotFoundError:
            return HttpResponseRedirect(f"{settings.REACT_APP_URL[0]}")

# Base ViewSet that Require login
class LoginRequiredViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]


# Base ViewSet that automatically set current user to owner
class AutoUserViewSet(LoginRequiredViewSet):
    def perform_create(self, serializer):
        # The request user is set as author automatically.
        serializer.save(owner=self.request.user)


class TrxAccountViewSet(AutoUserViewSet):
    """
    A simple ViewSet for viewing and editing the TrxAccount
    associated with the user.
    """
    serializer_class = TrxAccountSerializers

    def get_queryset(self):
        user = self.request.user
        trxact = User.objects.get(username='trxact')
        return TrxAccount.objects.filter(owner__in=[user.id, trxact])


class TrxAccountChoicesViewSet(AutoUserViewSet):
    """
    A simple ViewSet for viewing and editing the TrxAccountChoices
    associated with the user.
    """
    serializer_class = TrxAccountChoicesSerializers

    def get_queryset(self):
        user = self.request.user
        return TrxAccountChoices.objects.filter(owner=user.id)


class PeriodPreferenceViewSet(AutoUserViewSet):
    """
    A simple ViewSet for viewing and editing the PeriodPreference
    associated with the user.
    """
    serializer_class = PeriodPreferenceSerializers

    def get_queryset(self):
        user = self.request.user
        return PeriodPreference.objects.filter(owner=user.id)


class PeriodViewSet(AutoUserViewSet):
    """
    A simple ViewSet for viewing and editing the Period
    associated with the user.
    """
    serializer_class = PeriodSerializers

    def get_queryset(self):
        user = self.request.user
        return Period.objects.filter(owner=user.id)


class TransactionViewSet(LoginRequiredViewSet):
    """
    A simple ViewSet for viewing and editing the Transaction
    associated with the user.
    """
    serializer_class = TransactionSerializers
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['period', 'type']

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(period__owner=user.id)


class JournalViewSet(LoginRequiredViewSet):
    """
    A simple ViewSet for viewing and editing the Journal
    associated with the user.
    """
    serializer_class = JournalSerializers

    def get_queryset(self):
        user = self.request.user
        return Journal.objects.filter(transaction__period__owner=user.id)
