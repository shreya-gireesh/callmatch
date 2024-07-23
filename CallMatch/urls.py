"""
URL configuration for CallMatch project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from AdminApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login', views.login, name='login'),
    path('reg', views.reg, name='reg'),
    path('users', views.registered_users, name='users'),
    path('add_user', views.add_user, name='add_user'),
    path('delete_user', views.delete_user, name='delete_user'),
    path('wallet_normal_user', views.wallet_normaluser, name='wallet_normal_users'),
    path('history_normal_user', views.user_history, name='history_normal_users'),
    path('wallet_agent_user', views.wallet_agentuser, name='wallet_agent_users'),
    path('history_agent_user', views.agent_history, name='history_agent_users'),
    path('all_agents', views.report, name='agent_report'),
    path('coin_package', views.coin_package, name='coin_package'),
    path('agora/token/', views.get_agora_token, name='get_agora_token'),

    #api
    path('login_user/', views.customers, name='user_data'),
    path('all_users/', views.all_users, name='all_users'),
    path('update_profile/<int:id>', views.update_profile, name='update_profile'),
    path('wallet/<int:id>', views.wallet, name='wallet'),
    path('withdrawal/<int:id>', views.withdrawal, name='withdrawal'),
    path('start-call/', views.start_call, name='start-call'),
    path('end-call/', views.end_call, name='end-call'),
    path('chat_purchase/', views.buy_chat_package, name='chat_package'),
    path('call_purchase/', views.buy_call_package, name='call_package'),
    path('chat_package/', views.list_chat_packages, name='chat_packages'),
    path('call_package/', views.list_call_packages, name='call_packages'),
    path('send_message/', views.send_message, name='send_message'),
]
