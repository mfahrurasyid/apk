import csv
from django.contrib.auth.models import User
import os
from journal.models import TrxAccount, TrxAccountChoices


def run():
    admin = User.objects.create_superuser('mfahrur', 'mfahrurashyid@gmail.com', 'mfahrur')
    trxact = User.objects.create_user('trxact', 'trxact@gmail.com', 'trxact')
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(__location__, 'xx.csv')) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            trx = TrxAccount.objects.create(code=row[0], name=row[1], owner=trxact)
            TrxAccountChoices.objects.create(trx_acct=trx, owner=admin)
