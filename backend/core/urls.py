from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.create_entry, name='create_entry'),
    path('water/<int:entry_id>/', views.water_entry, name='water_entry'),
    path('entry/<int:entry_id>/view/', views.view_entry, name='view_entry'),
    path('entry/<int:entry_id>/edit/', views.edit_entry, name='edit_entry'),
    path('entry/<int:entry_id>/delete/', views.delete_entry, name='delete_entry'),
    path('renew/<int:entry_id>/', views.renew_entry, name='renew_entry'),
    path('god-message/', views.god_message, name='god_message'),




]
