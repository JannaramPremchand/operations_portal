from django.contrib import admin
from django.urls import path , include
from portal.views import save_createmeetings

urlpatterns = [
    path('save_createmeetings',save_createmeetings ),
]
