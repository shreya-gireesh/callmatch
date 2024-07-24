from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class AdminModel(models.Model):
    admin_id = models.AutoField(primary_key = True)
    admin_first_name = models.CharField(max_length=100)
    admin_last_name = models.CharField(max_length=100, null=True)
    admin_mail = models.EmailField()
    admin_password = models.CharField(max_length=100)

    def __str__(self):
        return self.admin_first_name


class CustomerModel(models.Model):
    NORMAL_USER = 'Normal User'
    AGENT_USER = 'Agent User'
    USER_STATUS_CHOICES = [
        (NORMAL_USER, 'Normal User'),
        (AGENT_USER, 'Agent User'),
    ]
    BOTH = 'Both'
    MALAYALAM = 'Malayalam'
    TAMIL = 'Tamil'
    LANGUAGE_CHOICES = [
        (BOTH, 'Both'),
        (MALAYALAM, 'Malayalam'),
        (TAMIL, 'Tamil'),
    ]
    customer_id = models.AutoField(primary_key = True)
    customer_first_name = models.CharField(max_length=100)
    customer_last_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_contact = models.CharField(max_length=50)
    status = models.CharField(
        max_length=20,
        choices=USER_STATUS_CHOICES,
        default=NORMAL_USER,
    )
    is_online = models.BooleanField(default=False)
    languages = models.CharField(
        max_length=20,
        choices=LANGUAGE_CHOICES,
        default=BOTH,
    )

    def __str__(self):
        return f"{self.customer_first_name} {self.customer_last_name}"


class WalletModel(models.Model):
    wallet_id = models.AutoField(primary_key = True)
    user = models.ForeignKey(CustomerModel, on_delete=models.CASCADE)
    wallet_coins = models.IntegerField(default=300, null=True)
    messages_remaining = models.IntegerField(default=0)  # For normal users
    call_amount = models.FloatField(default=0.0)
    chat_amount = models.FloatField(default=0.0)
    total_messages_received = models.IntegerField(default=0)
    total_minutes = models.IntegerField(default=0)
    total_amount = models.FloatField(default=0.0)


class UserPurchaseModel(models.Model):
    userpurchase_id = models.AutoField(primary_key = True)
    user = models.ForeignKey(CustomerModel, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField()
    purchase_amount = models.FloatField()


class WithdrawalHistoryModel(models.Model):
    agentpurchase_id = models.AutoField(primary_key = True)
    agent = models.ForeignKey(CustomerModel, on_delete=models.CASCADE)
    withdrawal_amount = models.FloatField()
    withdrawal_date = models.DateTimeField()




class CoinPackageModel(models.Model):
    coin_id = models.AutoField(primary_key = True)
    package_price = models.FloatField()
    total_coins = models.IntegerField()



class ChatPackageModel(models.Model):
    chat_id = models.AutoField(primary_key = True)
    package_price = models.FloatField()
    message_count = models.IntegerField()


# chat
class InboxModel(models.Model):
    inbox_id = models.AutoField(primary_key = True)
    last_message = models.TextField()
    last_sent_user = models.ForeignKey(CustomerModel, on_delete=models.CASCADE)


class InboxParticipantsModel(models.Model):
    message_id = models.AutoField(primary_key = True)
    inbox = models.ForeignKey(InboxModel, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomerModel, on_delete=models.CASCADE)


class MessageModel(models.Model):
    message_id = models.AutoField(primary_key = True)
    inbox = models.ForeignKey(InboxModel, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomerModel, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField()


# call details
class CallDetailsModel(models.Model):
    call_id = models.AutoField(primary_key=True)
    caller = models.ForeignKey(CustomerModel, related_name='caller', on_delete=models.CASCADE)
    agent = models.ForeignKey(CustomerModel, related_name='agent', on_delete=models.CASCADE)
    agora_channel_name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(default=0)  # Duration in minutes


class AgentTransactionModel(models.Model):
    CHAT = 'Chat'
    CALL = 'Call'
    TRANSACTION_TYPE_CHOICES = [
        (CHAT, 'Chat'),
        (CALL, 'Call'),
    ]
    agent_transaction_id = models.AutoField(primary_key = True)
    agent = models.ForeignKey(CustomerModel, on_delete=models.CASCADE)
    receiver = models.ForeignKey(CustomerModel, on_delete=models.CASCADE, related_name='received_transactions', null=True)
    transaction_amount = models.FloatField()
    transaction_date = models.DateTimeField()
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES, null=True)

    def __str__(self):
        return f"{self.agent.customer_first_name} {self.agent.customer_last_name}"