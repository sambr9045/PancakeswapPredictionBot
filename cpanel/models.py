from email.policy import default
from pyexpat import model
from django.db import models

# Create your models here.
from django.utils import timezone


class pancakeswapPredicition(models.Model):
    epoch = models.IntegerField(default=None, unique=True)
    bull = models.FloatField(default=None)
    bear = models.FloatField(default=None)
    wallet_number = models.IntegerField(default=None)
    transaction_hash = models.TextField(default="")
    claimable = models.BooleanField(default=False)
    claimed = models.BooleanField(default=False)
    wallet_balance = models.FloatField(default=0.0)
    bet_type = models.CharField(max_length=200, default=None)
    created_at = models.DateTimeField(default=timezone.now)


class server_status(models.Model):
    status = models.BooleanField(default=False)
    logging = models.TextField(default=None)
    started_at = models.DateTimeField(default=None, null=True)
    stoped_at = models.DateTimeField(default=None, null=True)
    updated_at = models.DateTimeField(default=None, null=True)
    created_at = models.DateTimeField(default=timezone.now)


class message_logging(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    message = models.TextField(default=None)
