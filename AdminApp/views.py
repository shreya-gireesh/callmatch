from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from .utils import generate_agora_token
from .serializer import *
from .models import *


# Create your views here.
def login(request):
    return render(request, 'login.html')


def register(request):
    return render(request, 'register.html')


def home(request):
    return render(request, 'index.html')


def registered_users(request):
    users = CustomerModel.objects.all()
    if request.method == 'POST':
        userid = request.POST.get('user_id')
        new_status = request.POST.get('status')
        user = CustomerModel.objects.get(customer_id=userid)
        user.status = new_status
        user.save()
        wallet = WalletModel.objects.get(user=userid)
        if new_status == 'Normal User':
            wallet.wallet_coins = 1000
            wallet.purchase_date = None
            wallet.agent_balance = 0
            wallet.save()
        elif new_status == 'Agent User':
            wallet.wallet_coins = 0
            wallet.purchase_date = None
            wallet.save()
    return render(request, 'registered_users.html', {'users': users})


def wallet_normaluser(request):
    wallets = WalletModel.objects.filter(user__status='Normal User')
    return render(request, 'normaluser_wallet.html', {'wallets': wallets})


def wallet_agentuser(request):
    wallets = WalletModel.objects.filter(user__status='Agent User')
    return render(request, 'agentuser_wallet.html', {'wallets': wallets})


def agent_history(request):
    agent_history = AgentPurchaseModel.objects.all()
    return render(request, 'agentuser_history.html', {'agent_history': agent_history})


def coin_package(request):
    coins = CoinsModel.objects.all()
    return render(request, 'coin_package.html', {'coins': coins})


def get_agora_token(request):
    channel_name = request.GET.get('channelName')
    uid = request.GET.get('uid')
    role = request.GET.get('role', 1)  # Default role is 1 (Attendee)
    expiration_time_in_seconds = int(request.GET.get('expiry', 3600))  # Default to 1 hour

    if not channel_name or not uid:
        return JsonResponse({'error': 'Channel name and uid are required'}, status=400)

    token = generate_agora_token(channel_name, uid, role, expiration_time_in_seconds)
    return JsonResponse({'token': token})


# api
@api_view(['GET'])
def customers(request):
    email = request.data.get('email')
    password = request.data.get('password')
    if not email or not password:
        return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = CustomerModel.objects.get(customer_email=email, customer_password=password)
    except CustomerModel.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    user_data = CustomerSerializer(user)
    return Response(user_data.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def wallet(request, id):
    wallet = WalletModel.objects.get(user=id)
    wallet_data = WalletSerializer(wallet, many=False)
    return Response(wallet_data.data)


@api_view(['GET'])
def report(request, id):
    agent = AgentPurchaseModel.objects.get(user=id)
    agent_data = AgentPurchaseSerializer(agent).data
    wallet = WalletModel.objects.get(user=id)
    wallet_data = WalletSerializer(wallet).data
    reports = {**agent_data, **wallet_data}
    return Response(reports)


@api_view(['GET'])
def coins(request):
    coins = CoinsModel.objects.all()
    coins_data = CoinsSerializer(coins, many=True)
    return Response(coins_data.data)