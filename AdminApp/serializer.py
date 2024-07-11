from rest_framework import serializers
from .models import *


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerModel
        fields = '__all__'


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletModel
        fields = '__all__'


class AgentPurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentPurchaseModel
        fields = '__all__'


class CoinsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinsModel
        fields = '__all__'