from django.contrib import admin
from django.urls import path, include
from locks import views

urlpatterns = [
    path('', views.lock_index, name="lock_index"),
    path('<int:id>', views.lock_detail, name="lock_detail"),
    path('api/', views.LockView.as_view())
]