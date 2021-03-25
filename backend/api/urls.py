from django.conf.urls import url
from rest_framework.authtoken import views as drf_views
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register(r'trx-accounts', TrxAccountViewSet, basename='trx-accounts')
router.register(r'trx-account-choices', TrxAccountChoicesViewSet, basename='trx-account-choices')
router.register(r'period-preference', PeriodPreferenceViewSet, basename='period-preference')
router.register(r'period', PeriodViewSet, basename='period')
router.register(r'transactions', TransactionViewSet, basename='transactions')

urlpatterns = [
    url(r'^auth/$', drf_views.obtain_auth_token, name='auth'),
]

urlpatterns += router.urls