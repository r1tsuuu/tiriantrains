from django.contrib.auth import views as auth_views
from django.urls import path
from apps.home import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),

    path('pages-tickets.html', views.ticket_sales, name='ticket_sales'),

    path('pages-summary.html', views.ticket_summary, name='ticket_summary'),

    path('pages-profile.html', views.profile, name='profile'),

    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    path('register/', views.register, name='register'),

    path('login/', views.login_view, name='login'),
]
