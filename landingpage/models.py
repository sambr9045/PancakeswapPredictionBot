import ipaddress
from django.db import models
import uuid
from django.utils import timezone

# Create your models here.
class validate(models.Model):
    token = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.IntegerField(blank=False)
    attempt = models.IntegerField(default=0, blank=1)
    validate = models.BooleanField(default=False)
    email = models.EmailField(blank=False)
    updated_at = models.DateTimeField(default=timezone.now, blank=True)
    created_at = models.DateTimeField(default=timezone.now)


# login failed attemps
class loginAttempts(models.Model):
    ipaddress = models.CharField(null=False, blank=False, max_length=50)
    attempt = models.IntegerField(null=False)
    updated_at = models.DateTimeField(default=timezone.now, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
