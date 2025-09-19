from django.urls import path, include
from rest_framework import routers
from rest_framework_nested import routers as nested_routers
from .views import ConversationViewSet, MessageViewSet


# Create a router and register our viewsets with it.
router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
# keep a top-level messages endpoint as well
router.register(r'messages', MessageViewSet, basename='message')

# Nested router to list/create messages under a specific conversation:
conversation_router = nested_routers.NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversation_router.register(r'messages', MessageViewSet, basename='conversation-messages')

# The API URLs are now determined automatically by the router and nested router.
urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversation_router.urls)),
]