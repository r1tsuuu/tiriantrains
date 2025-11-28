# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth import views as auth_views
from django.urls import path, re_path
from apps.home import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),

    path('pages-tickets.html', views.ticket_sales, name='ticket_sales'),

    path('pages-summary.html', views.ticket_summary, name='ticket_summary'),

    path('pages-profile.html', views.profile, name='profile'),

    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
