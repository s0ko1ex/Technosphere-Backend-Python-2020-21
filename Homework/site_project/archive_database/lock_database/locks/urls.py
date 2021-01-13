from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.lock_index, name="lock_index"),
    path('<int:id>', views.lock_detail, name="lock_detail")
]