from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    is_unit_manager = models.BooleanField(default=False)
    is_senior_manager = models.BooleanField(default=False)
    is_hod = models.BooleanField(default=False)
    is_ceo = models.BooleanField(default=False)
    signature = models.ImageField(upload_to='signature_images/', null=True, blank=True)