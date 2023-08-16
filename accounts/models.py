from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class Department(models.Model):
    name = models.CharField(max_length=50)
    hod = models.OneToOneField('CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='department_hod')

class Unit(models.Model):
    name = models.CharField(max_length=50)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='units')
    unit_manager = models.OneToOneField('CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_unit')

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    is_unit_manager = models.BooleanField(default=False)
    is_senior_manager = models.BooleanField(default=False)
    is_hod = models.BooleanField(default=False)
    is_ceo = models.BooleanField(default=False)
    signature = models.ImageField(upload_to='signature_images/', null=True, blank=True)  # Use ImageField for the drawn signature
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='department_users')
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True, related_name='unit_users')

class PurchaseRequisition(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchase_requests')
    reason_for_request = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Total amount for all items
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)
    currency = models.CharField(max_length=3, choices=[("USD", "USD"), ("RWF", "RWF")], default="RWF")

    def save(self, *args, **kwargs):
        if self.pk is None:  # New instance
            super().save(*args, **kwargs)  # Save to get a primary key

            # Calculate and update total_amount after saving
            total_amount = sum(item.total_price for item in self.items.all())
            self.total_amount = total_amount
            super().save(*args, **kwargs)  # Update total_amount

        else:  # Existing instance
            super().save(*args, **kwargs)

    def __str__(self):
        return f"Purchase Requisition by {self.user.username}"

class PurchaseItem(models.Model):
    requisition = models.ForeignKey(PurchaseRequisition, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
