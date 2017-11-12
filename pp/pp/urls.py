
from django.conf.urls import url
from django.contrib import admin

from pp.pp.views import annotations


import views

urlpatterns = [
    url(r'^', annotations.get),

]

