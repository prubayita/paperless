from django.db import models
# from django.contrib.auth.models import User

# # Create your models here.

# class Item(models.Model):
#     name= models.CharField(max_length=50)
#     unit_price = models.DecimalField(max_digits=20, decimal_places=2)
    

#     def __str__(self):
#         return self.name



# class Purchasereq(models.Model):
#     requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_purchasereqs')
#     unit_manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='unit_managed_purchasereqs')
#     senior_manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='senior_manager_purchasereqs')
#     hod = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hod_purchasereqs')
#     # unit_price = models.ForeignKey(Item, on_delete=models.CASCADE)
#     total_price= models.DecimalField(max_digits=20, decimal_places=2)
#     quantity = models.IntegerField()
#     reason= models.CharField(max_length=50)
