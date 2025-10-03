from django.urls import path
from .auth import CustomTokenObtainPairView, CustomTokenRefreshView
 
from .views import conversation_detail, conversation_list_create, message_list_create, message_detail
urlpatterns = [
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path("conversations/", conversation_list_create, name="conversation-list"),
    path(
        "conversations/<uuid:conversation_id>/messages/",
        message_list_create,
        name="conversation-messages",
    ),
    path(
        "conversations/<uuid:conversation_id>/",
        conversation_detail,
        name="conversation-detail",
    ),
    path("messages/", message_list_create, name="message-list"),
    path("messages/<uuid:message_id>/", message_detail, name="message-detail"),
]
