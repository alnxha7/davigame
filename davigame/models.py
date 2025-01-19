from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    location = models.CharField(max_length=225)
    mobile = models.CharField(max_length=15)  
    is_approved = models.BooleanField(default=False)
    davitokens = models.IntegerField(default=0)
    wallet_amount = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.email}"
    
class Davitokens(models.Model):
    amount = models.IntegerField(blank=True, null=True)
    davitokens = models.IntegerField(blank=True, null=True)
    image = models.ImageField(upload_to='davitokens/')
    released = models.DateTimeField(null=True)

class DaviPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField(null=True, blank=True)
    davitokens = models.IntegerField(blank=True, null=True)
    card_number = models.IntegerField()
    cvv = models.IntegerField()
    date = models.DateTimeField()

class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField(null=True, blank=True)
    davitokens = models.IntegerField(blank=True, null=True)
    account_number = models.IntegerField()
    ifsc_code = models.CharField(max_length=15)
    date = models.DateTimeField()

class DaviConvertion(models.Model):
    davitokens = models.IntegerField(blank=True, null=True)
    amount = models.IntegerField(blank=True, null=True)