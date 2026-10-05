"""
URL routing for accounts app.
"""
from django.urls import path
from apps.accounts.views import RegisterView, LoginView, RefreshTokenView, MeView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("refresh/", RefreshTokenView.as_view(), name="auth-refresh"),
    path("me/", MeView.as_view(), name="auth-me"),
]
