from django.contrib import admin
from django.urls import path

from registration import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("register/", views.form_page, name="form"),
    path("api/submissions/", views.create_submission, name="create_submission"),
]