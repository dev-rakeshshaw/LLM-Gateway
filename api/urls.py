from django.urls import path

from .views import ChatCompletionView

urlpatterns = [
    path(
        "chat/completions/",
        ChatCompletionView.as_view(),
        name="chat-completions",
    ),
]