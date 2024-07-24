import requests
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse, HttpResponseNotAllowed
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST
from django.db.models import Q
from CallMatch import settings
from .utils import generate_agora_token
from django.utils import timezone
from datetime import datetime
from .forms import CustomerForm, AdminForm
from .serializer import *
from .models import *


MESSAGE_COST = 0.25  # Cost per message to agent


# Create your views here.
def report(request):
    agents = CustomerModel.objects.filter(status ='Agent User' )
    report_data = {}
    if request.method == 'POST':
        agent_id = request.POST.get('agent_id')
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')

        from_date = parse_date(from_date) if from_date else None
        to_date = parse_date(to_date) if to_date else None

        if not agent_id or not from_date or not to_date:
            return JsonResponse({'error': 'Agent, from date, and to date are required'}, status=400)

        agent = get_object_or_404(CustomerModel, customer_id=agent_id)
        wallet = WalletModel.objects.get(user__customer_id=agent_id)
        withdrawals = WithdrawalHistoryModel.objects.filter(agent=agent, withdrawal_date__range=[from_date, to_date])
        transactions = AgentTransactionModel.objects.filter(agent=agent, transaction_date__range=[from_date, to_date])
        wallet_data = {
            'call_amount': wallet.call_amount if wallet else 0,
            'chat_amount': wallet.chat_amount if wallet else 0,
            'total_messages_received': wallet.total_messages_received if wallet else 0,
            'total_minutes': wallet.total_minutes if wallet else 0,
            'total_amount': wallet.total_amount if wallet else 0,
        }
        withdrawal_data = [
            {
                'withdrawal_amount': w.withdrawal_amount,
                'withdrawal_date': w.withdrawal_date.strftime('%d %B %Y %I:%M %p')
            }
            for w in withdrawals
        ]
        transactions_data = [
            {
                "receiver": f"{t.receiver.customer_first_name} {t.receiver.customer_last_name}",
                "amount": t.transaction_amount,
                "date":  t.transaction_date.strftime('%d %B %Y %I:%M %p'),
                "type":t.transaction_type
            }
            for t in transactions
        ]
        report_data = {
            'agent_name': f"{agent.customer_first_name} {agent.customer_last_name}",
            'wallet': wallet_data,
            'transactions': transactions_data,
            'withdrawals': withdrawal_data,
        }
        return JsonResponse(report_data, status=200)
    return render(request, 'agent_report.html', {'agents': agents})


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            admin = AdminModel.objects.get(admin_mail=email, admin_password=password)
            admin_name = f"{admin.admin_first_name} {admin.admin_last_name}"
            request.session['user'] = admin_name
            request.session.set_expiry(600)

            expiry = request.session.get_expiry_age()
            print(f"Session will expire in {expiry} seconds")

            return redirect('/')
        except AdminModel.DoesNotExist:
            return render(request, 'login.html', {'error': "User not found"})
    return render(request, 'login.html')


def reg(request):
    if request.method == 'POST':
        form = AdminForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login page after successful registration
        else:
            print(form.errors)
    else:
        form = AdminForm()
    return render(request, 'register.html', {'form': form})


def home(request):
    username = request.session.get('user', None)
    if username is None:
        return redirect('/login')
    else:
        normal_users_count = CustomerModel.objects.filter(status='Normal User').count
        agent_user_count = CustomerModel.objects.filter(status='Agent User').count
        all_agents = CustomerModel.objects.filter(status = 'Agent User')
    return render(request, 'index.html', {'normaluser': normal_users_count, 'agentuser': agent_user_count,
                                          'all_agents': all_agents, 'username': username})


@require_POST
def toggle_online_status(request, customer_id):
    try:
        customer = CustomerModel.objects.get(pk=customer_id)
        customer.is_online = False
        customer.save()
        return JsonResponse({'success': True})
    except CustomerModel.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Customer not found'})


def registered_users(request):
    username = request.session.get('user', None)
    if username is None:
        return redirect('/login')
    else:
        users = CustomerModel.objects.all()
        if request.method == 'POST':
            userid = request.POST.get('user_id')
            new_status = request.POST.get('status')
            user = CustomerModel.objects.get(customer_id=userid)
            user.status = new_status
            user.save()
            wallet = WalletModel.objects.get(user=userid)

            if new_status == 'Normal User':
                wallet.wallet_coins = 300
                wallet.purchase_date = None
                wallet.agent_balance = 0
                wallet.save()
            elif new_status == 'Agent User':
                wallet.wallet_coins = 0
                wallet.purchase_date = None
                wallet.save()

    return render(request, 'registered_users.html', {'users': users, 'username': username})


def add_user(request):
    username = request.session.get('user', None)
    if username is None:
        return redirect('/login')
    else:
        if request.method == 'POST':
            form = CustomerForm(request.POST)
            if form.is_valid():
                form.save()  # Saves the form data to the CustomerModel database table
                return redirect('users')  # Redirect to a success page or another view after successful submission
        else:
            form = CustomerForm()
    return render(request, 'add_user.html', {'form': form, 'username': username})


def delete_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if user_id:
            try:
                user = CustomerModel.objects.get(pk=user_id)
                user.delete()
                return redirect('users')  # Redirect to the users list page after deletion
            except CustomerModel.DoesNotExist:
                return redirect('users')  # Handle the case where the user does not exist
    return HttpResponseNotAllowed(['POST'])


def wallet_normaluser(request):
    username = request.session.get('user', None)
    if username is None:
        return redirect('/login')
    wallets = WalletModel.objects.filter(user__status='Normal User')
    return render(request, 'normaluser_wallet.html', {'wallets': wallets, 'username': username})


def wallet_agentuser(request):
    username = request.session.get('user', None)
    if username is None:
        return redirect('/login')

    wallets = WalletModel.objects.filter(user__status='Agent User')
    return render(request, 'agentuser_wallet.html', {'wallets': wallets, 'username': username})


def user_history(request):
    username = request.session.get('user', None)
    if username is None:
        return redirect('/login')

    user_history = UserPurchaseModel.objects.all()
    return render(request, 'normaluser_history.html', {'user_history': user_history, 'username': username})


def agent_history(request):
    username = request.session.get('user', None)
    if username is None:
        return redirect('/login')

    agent_history = WithdrawalHistoryModel.objects.all()
    return render(request, 'agentuser_history.html', {'agent_history': agent_history, 'username': username})


def coin_package(request):
    username = request.session.get('user', None)
    if username is None:
        return redirect('/login')
    coins = CoinPackageModel.objects.all()
    chats = ChatPackageModel.objects.all()
    return render(request, 'coin_package.html', {'coins': coins,'chats': chats, 'username': username})


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
@api_view(['POST'])
def customers(request):
    contact = request.data.get('mobile_no')
    if not contact:
        return Response({'error': 'Phone Number required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomerModel.objects.get(customer_contact=contact)
    except CustomerModel.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

    user.is_online = True
    user.save()
    user_data = CustomerSerializer(user)
    return Response(user_data.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def all_users(request):
    users = CustomerModel.objects.filter(status = CustomerModel.AGENT_USER)
    user_data = CustomerSerializer(users, many=True)
    return Response(user_data.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def update_profile(request, id):
    user = CustomerModel.objects.get(customer_id = id)
    user_data = CustomerSerializer(instance=user, data=request.data, partial = True)
    if user_data.is_valid():
        user_data.save()
        return Response({"message": "Profile updated successfully"})
    return Response(user_data.errors)


@api_view(['POST'])
def register(request):
    contact = request.data.get('mobile_no')
    if not contact:
        return Response({'error': 'Phone Number required'}, status=status.HTTP_400_BAD_REQUEST)

    user, created = CustomerModel.objects.get_or_create(
        customer_contact=contact,
        defaults={
            'customer_first_name': request.data.get('first_name', ''),
            'customer_last_name': request.data.get('last_name', ''),
            'customer_email': request.data.get('email', ''),
        }
    )

    if created:
        user.is_online = True
        user.save()
        user_data = CustomerSerializer(user)
        return Response(user_data.data, status=status.HTTP_201_CREATED)
    else:
        return Response({'error': 'Customer already exists'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def wallet(request, id):
    wallet = WalletModel.objects.get(user=id)
    wallet_data = WalletSerializer(wallet, many=False)
    return Response(wallet_data.data)


@api_view(['GET'])
def withdrawal(request, id):
    agent = WalletModel.objects.get(user__customer_id=id)

    if agent.total_amount >= 5000:
        withdrawal_amount = agent.total_amount
        agent.total_amount = agent.total_amount - withdrawal_amount
        print(agent.total_amount)
        agent.save()
        WithdrawalHistoryModel.objects.create(
            agent=CustomerModel.objects.get(customer_id= id),
            withdrawal_amount=withdrawal_amount,
            withdrawal_date=datetime.now()
        )

        return JsonResponse({'message': f'Withdrawn amount: {withdrawal_amount}'}, status=200)
    else:
        # Return error response if balance is insufficient
        return JsonResponse({'error': 'Insufficient balance for withdrawal'}, status=400)


# call
@api_view(['POST'])
def start_call(request):
    caller_id = request.data.get('caller_id')
    agent_id = request.data.get('agent_id')
    agora_channel_name = request.data.get('agora_channel_name')

    call = CallDetailsModel.objects.create(
        caller_id=caller_id,
        agent_id=agent_id,
        agora_channel_name=agora_channel_name,
        start_time=timezone.now()
    )

    return Response({"call_id": call.call_id})


@api_view(['POST'])
def end_call(request):
    call_id = request.data.get('call_id')

    call = CallDetailsModel.objects.get(call_id=call_id)
    call.end_time = timezone.now()
    call.save()

    # Fetch call duration from Agora API
    agora_app_id = settings.AGORA_APP_ID
    agora_app_certificate = settings.AGORA_APP_CERTIFICATE
    agora_api_url = f'https://api.agora.io/dev/v1/channel/{agora_app_id}/{call.agora_channel_name}?token={agora_app_certificate}'

    response = requests.get(agora_api_url)
    call_data = response.json()

    if 'duration' in call_data:
        duration = call_data['duration'] // 60  # Convert seconds to minutes
        call.duration = duration
        call.save()

        caller_wallet = WalletModel.objects.get(user=call.caller)
        agent_purchase = WalletModel.objects.get(user=call.agent)

        cost_per_minute = 150
        amount_per_minute = 3

        # Deduct coins from caller
        caller_wallet.wallet_coins -= duration * cost_per_minute
        caller_wallet.save()

        # Add amount to agent's balance
        agent_purchase.call_amount += duration * amount_per_minute
        agent_purchase.total_minutes += duration
        agent_purchase.total_amount = agent_purchase.total_amount + (duration * amount_per_minute)
        agent_purchase.save()

        # Create transaction record
        AgentTransactionModel.objects.create(
            agent=agent_purchase,
            receiver= call.caller,
            transaction_amount=amount_per_minute,
            transaction_date=datetime.now(),
            transaction_type='Call'
        )

        return Response({"duration": duration})
    else:
        return Response({"error": "Failed to fetch call duration from Agora API"}, status=500)


@api_view(['GET'])
def list_chat_packages(request):
    packages = ChatPackageModel.objects.all()
    serializer = PackageSerializer(packages, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def list_call_packages(request):
    packages = CoinPackageModel.objects.all()
    serializer = CoinsSerializer(packages, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['POST'])
def buy_chat_package(request):
    user_id = request.data.get('user_id')
    package_id = request.data.get('package_id')

    try:
        user = CustomerModel.objects.get(pk=user_id, status=CustomerModel.NORMAL_USER)
        package = ChatPackageModel.objects.get(pk=package_id)
    except (CustomerModel.DoesNotExist, ChatPackageModel.DoesNotExist):
        return Response({'error': 'User or package not found'}, status=status.HTTP_404_NOT_FOUND)

    # Add messages to user
    wallet = WalletModel.objects.get(user=user_id)
    wallet.messages_remaining += package.message_count
    wallet.save()

    purchase_date = datetime.now()
    history = UserPurchaseModel.objects.create(
        user = user,
        purchase_amount = package.package_price,
        purchase_date=purchase_date
    )

    return Response({'message': 'Package purchased successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def buy_call_package(request):
    user_id = request.data.get('user_id')
    package_id = request.data.get('package_id')

    try:
        user = CustomerModel.objects.get(pk=user_id, status=CustomerModel.NORMAL_USER)
        package = CoinPackageModel.objects.get(pk=package_id)
    except (CustomerModel.DoesNotExist, CoinPackageModel.DoesNotExist):
        return Response({'error': 'User or package not found'}, status=status.HTTP_404_NOT_FOUND)

    # Add messages to user
    wallet = WalletModel.objects.get(user=user_id)
    wallet.wallet_coins += package.total_coins
    wallet.save()

    purchase_date = datetime.now()
    history = UserPurchaseModel.objects.create(
        user=user,
        purchase_amount=package.package_price,
        purchase_date = purchase_date
    )

    return Response({'message': 'Package purchased successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def send_message(request):
    user_1 = request.data.get('user_1')
    user_2 = request.data.get('user_2')
    message_text = request.data.get('message')

    if not user_1 or not user_2 or not message_text:
        return Response({'error': 'Users, and message are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user1= CustomerModel.objects.get(customer_id=user_1)
        print(user1)
        user2 = CustomerModel.objects.get(customer_id=user_2)
        print(user2)
    except CustomerModel.DoesNotExist:
        return Response({'error': 'User or agent not found'}, status=status.HTTP_404_NOT_FOUND)

    # Check if the sender is the user or the agent
    sender = user1
    recipient = user2

    if sender.status == 'Normal User':
        user_wallet = WalletModel.objects.get(user=user1)
        if user_wallet.messages_remaining <= 0:
            return Response({'error': 'Not enough messages remaining'}, status=status.HTTP_400_BAD_REQUEST)
        # Deduct message from user's wallet
        user_wallet.messages_remaining -= 1
        user_wallet.save()

    # Add amount to agent's account if the sender is the user
    if recipient.status == 'Agent User':
        agent_wallet, created = WalletModel.objects.get_or_create(user=user2)
        agent_wallet.chat_amount += MESSAGE_COST
        agent_wallet.total_messages_received += 1
        agent_wallet.total_amount = agent_wallet.total_amount + MESSAGE_COST
        agent_wallet.save()

        # Create transaction record
        AgentTransactionModel.objects.create(
            agent=recipient,
            receiver=sender,
            transaction_amount=MESSAGE_COST,
            transaction_date = datetime.now(),
            transaction_type='Chat'
        )

    inbox, created = InboxModel.objects.get_or_create(
        last_sent_user=sender,
        defaults={'last_message': message_text}
    )
    if not created:
        inbox.last_message = message_text
        inbox.save()

    # Ensure both participants are in the inbox
    InboxParticipantsModel.objects.get_or_create(inbox=inbox, user=user1)
    InboxParticipantsModel.objects.get_or_create(inbox=inbox, user=user2)

    # Create the message
    message = MessageModel.objects.create(
        inbox=inbox,
        user=sender,
        message=message_text,
        created_at = datetime.now()
    )

    return Response({'message': 'Message sent successfully'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_chat(request, user1, user2):
    try:
        user_1 = CustomerModel.objects.get(customer_id=user1)
        user_2 = CustomerModel.objects.get(customer_id=user2)
    except CustomerModel.DoesNotExist:
        return Response({'error': 'User or agent not found'}, status=status.HTTP_404_NOT_FOUND)

    # if user.status != 'Normal User' or agent.status != 'Agent User':
    #     return Response({'error': 'Invalid user or agent status'}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch all messages in the inbox where both user and agent are participants
    messages = MessageModel.objects.filter(
        inbox__in=InboxParticipantsModel.objects.filter(user=user_1).values_list('inbox', flat=True),
        user__in=[user_1, user_2]
    ).order_by('created_at')

    # Serialize the messages
    serializer = MessageSerializer(messages, many=True)

    return Response({'messages': serializer.data}, status=status.HTTP_200_OK)
