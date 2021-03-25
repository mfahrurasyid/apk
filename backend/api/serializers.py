from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from .models import *


class TrxAccountSerializers(ModelSerializer):
    class Meta:
        model = TrxAccount
        exclude = ['owner', 'created_at', 'updated_at']


class TrxAccountChoicesSerializers(ModelSerializer):
    trx_acct = TrxAccountSerializers(many=False)

    class Meta:
        model = TrxAccountChoices
        exclude = ['owner', 'created_at', 'updated_at']


class PeriodPreferenceSerializers(ModelSerializer):
    class Meta:
        model = PeriodPreference
        exclude = ['owner', 'created_at', 'updated_at']


class PeriodSerializers(ModelSerializer):
    class Meta:
        model = Period
        exclude = ['owner', 'created_at', 'updated_at']

    def create(self, validated_data):
        start = validated_data.get('start')
        end = validated_data.get('end')
        if Period.objects.filter(start__lte=start).filter(end__gte=start):
            raise ValidationError(detail='Tanggal Awal berada di dalam rentang tanggal periode lain')
        if Period.objects.filter(start__lte=end).filter(end__gte=end):
            raise ValidationError(detail='Tanggal Akhir berada di dalam rentang tanggal periode lain')
        period = Period.objects.create(**validated_data)
        return period


class JournalSerializers(ModelSerializer):

    class Meta:
        model = Journal
        fields = ['id', 'amount', 'debt', 'account']


class TransactionSerializers(ModelSerializer):
    journal_set = JournalSerializers(many=True)

    class Meta:
        model = Transaction
        fields = ['id', 'time', 'name', 'journal_set']

    def check_available_period(self, time):
        period = Period.objects.filter(owner=self.context.get('request').user).filter(start__lte=time).filter(end__gte=time)
        if not period:
            raise ValidationError(detail='Tidak ada Periode Akuntansi yang cocok untuk tanggal transaksi tersebut')
        return period

    @staticmethod
    def check_journal_balance(journal_set):
        debt = 0
        credit = 0
        for journal in journal_set:
            if journal.get('debt') == "D":
                debt += journal.get('amount')
            elif journal.get('debt') == "C":
                credit += journal.get('amount')
        if debt != 0 and debt != credit:
            raise ValidationError(detail=f'Jurnal tidak seimbang, Debet: {debt} - Kredit: {credit}')

    def create(self, validated_data):
        journal_set = validated_data.pop('journal_set')
        time = validated_data['time']
        period = self.check_available_period(time)
        self.check_journal_balance(journal_set)
        transaction = Transaction.objects.create(period=period[0], **validated_data)
        for journal in journal_set:
            Journal.objects.create(transaction=transaction, **journal)
        return transaction
