from django.db import models


# Create your models here.
class CustomerModel(models.Model):
    NORMAL_USER = 'Normal User'
    AGENT_USER = 'Agent User'
    USER_STATUS_CHOICES = [
        (NORMAL_USER, 'Normal User'),
        (AGENT_USER, 'Agent User'),
    ]
    customer_id = models.AutoField(primary_key = True)
    customer_first_name = models.CharField(max_length=100)
    customer_last_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_contact = models.CharField(max_length=50)
    customer_password = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=USER_STATUS_CHOICES,
        default=NORMAL_USER,
    )

    def __str__(self):
        return f"{self.customer_first_name} {self.customer_last_name}"


class WalletModel(models.Model):
    wallet_id = models.AutoField(primary_key = True)
    user = models.ForeignKey(CustomerModel, on_delete=models.CASCADE)
    wallet_coins = models.IntegerField(default=1000, null=True)
    purchase_date= models.DateField(null=True, blank=True)
    agent_balance = models.IntegerField(default=0, null=True)


class AgentPurchaseModel(models.Model):
    agentpurchase_id = models.AutoField(primary_key = True)
    user = models.ForeignKey(CustomerModel, on_delete=models.CASCADE)
    total_amount = models.IntegerField(default=0)
    total_minutes = models.IntegerField(default=0)
    withdrawal_amount = models.IntegerField(default=0)


class CoinsModel(models.Model):
    coin_id = models.AutoField(primary_key = True)
    coin_amount = models.IntegerField()

