"""
URL configuration for davigame_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from davigame import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register_user', views.register_user, name='register_user'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_user, name='logout'),

    path('admin_index', views.admin_index, name='admin_index'),
    path('admin_davis', views.admin_davis, name='admin_davis'),
    path('manage_users', views.manage_users, name='manage_users'),
    path('davipayment_record', views.davipayment_record, name='davipayment_record'),

    path('user_index', views.user_index, name='user_index'),
    path('purchase_davis', views.purchase_davis, name='purchase_davis'),    
    path('davi_payment/<int:token_id>', views.davi_payment, name='davi_payment'),
    path('delete_token/<int:token_id>', views.delete_token, name='delete_token'),
    
    path('success', views.success, name='success'),
    path('cancel', views.cancel, name='cancel'),

    path('simon_game', views.simon_game, name='simon_game'),
    path('games', views.games, name='games'),
    path('user_payment', views.user_payment, name='user_payment'),
    path('simon_win', views.simon_win, name='simon_win'),

    path('mole_game', views.mole_game, name='mole_game'),
    path('mole_win', views.mole_win, name='mole_win'),
    path('user_wallet', views.user_wallet, name='user_wallet'),
    path('davi_conversion', views.davi_conversion, name='davi_conversion'),
    path('delete_conversion/<int:conv_id>', views.delete_conversion, name='delete_conversion'),
    
    path('wallet_transfer', views.wallet_transfer, name='wallet_transfer'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)