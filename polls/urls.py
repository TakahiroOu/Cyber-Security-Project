from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "polls"

urlpatterns = [
    path("", views.index, name="index"),

    path("login/", views.login_view, name="login"),

    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    path("<question_id>/", views.detail, name="detail"),
    # FIX2:
    # Restrict question_id to an integer:
    #
    # path("<int:question_id>/", views.detail, name="detail"),

    path("<int:question_id>/results/", views.results, name="results"),

    path("<int:question_id>/vote/", views.vote, name="vote"),
]