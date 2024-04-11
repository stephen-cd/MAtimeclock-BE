from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path("login/", LoginView.as_view(), name='login'),
    path("", views.index, name="index"),
    path("logout/", LogoutView.as_view(), name='logout'),
    path('update-db/', views.update_db, name='update_db')
]