from django.contrib import admin
from django.urls import path

from registration import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("register/", views.form_page, name="form"),
    path("agenda/", views.agenda_page, name="agenda"),
    path("api/submissions/", views.create_submission, name="create_submission"),
    path("api/mentors/", views.mentor_list, name="mentor_list"),
]