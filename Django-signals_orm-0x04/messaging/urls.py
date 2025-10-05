from django.urls import path

from . import views

urlpatterns = [
    path("messages/", views.message_list, name="message_list"),
    path("messages/<int:message_id>/", views.message_detail, name="message_detail"),
    path("messages/create/", views.message_create, name="message_create"),
    path("messages/<int:message_id>/edit/", views.message_edit, name="message_edit"),
    path("messages/<int:message_id>/delete/", views.delete_message, name="message_delete"),
    path("messages/<int:message_id>/mark-read/", views.message_mark_read, name="message_mark_read"),

    path("users/delete_user/<int:user_id>/", views.delete_user, name="user_delete"),
]
