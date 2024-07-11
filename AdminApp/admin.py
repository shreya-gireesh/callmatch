from django.contrib import admin
from AdminApp.models import *

# Register your models here.
admin.site.register(CustomerModel)
admin.site.register(WalletModel)
admin.site.register(AgentPurchaseModel)
admin.site.register(CoinsModel)