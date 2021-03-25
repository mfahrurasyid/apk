import uuid
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.urls import reverse


class BaseModel(models.Model):
    id = models.UUIDField(max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TrxAccount(BaseModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    code = models.IntegerField()

    class Meta:
        ordering = ['code']

    def __str__(self):
        return '%s - %s' % (self.code, self.name)

    def get_absolute_url(self):
        return reverse('trxaccount-detail', args=[str(self.id)])

    def get_update_url(self):
        return reverse('trxaccount-update', args=[str(self.id)])


class TrxAccountChoices(BaseModel):
    trx_acct = models.OneToOneField(TrxAccount, on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return '%s - %s' % (self.trx_acct.code, self.trx_acct.name)


class PeriodPreference(BaseModel):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start = models.DateField()
    end = models.DateField()

    def __str__(self):
        return '%s - %s' % (self.start, self.end)


class Period(BaseModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start = models.DateField()
    end = models.DateField()

    def __str__(self):
        return '%s - %s' % (self.start, self.end)


class Transaction(BaseModel):
    TYPES = [
        ('U', 'Umum'),
        ('S', 'Penyesuaian'),
        ('B', 'Pembalik'),
    ]
    period = models.ForeignKey(Period, on_delete=models.CASCADE, default=None, null=True, blank=True)
    type = models.CharField(max_length=2, choices=TYPES, default='U')
    time = models.DateField()
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('transaction-detail', args=[str(self.id)])

    def get_update_url(self):
        return reverse('transaction-update', args=[str(self.id)])

    def get_total_debt(self):
        return Journal.objects.filter(transaction=self).filter(debt='D').aggregate(Sum('amount'))['amount__sum'] or '0'

    def get_total_credit(self):
        return Journal.objects.filter(transaction=self).filter(debt='C').aggregate(Sum('amount'))['amount__sum'] or '0'

    def check_completed(self):
        if self.get_total_debt() != '0' and self.get_total_credit() != '0':
            return True
        else:
            return False


class Journal(BaseModel):
    TYPES = [
        ('D', 'Debt'),
        ('C', 'Credit'),
    ]

    amount = models.IntegerField()
    account = models.ForeignKey(TrxAccountChoices, on_delete=models.DO_NOTHING)
    debt = models.CharField(max_length=1, choices=TYPES, default='D')
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)

    class Meta:
        ordering = ['debt']

    def __str__(self):
        return '%s - %s' % (self.account.trx_acct.name, self.amount)

    def get_absolute_url(self):
        return reverse('journal-detail', args=[str(self.id)])

    def get_update_url(self):
        return reverse('journal-update', args=[str(self.id)])
