from django.apps import AppConfig


class PortfolioConfig(AppConfig):
    name = 'portfolio'

    def ready(self):
        from django.db.models.signals import post_delete, post_save

        from . import chatbot
        from .models import ChatAnswer

        # Admin edits to chat answers take effect on the next message.
        post_save.connect(chatbot.clear_cache, sender=ChatAnswer, dispatch_uid='chat-answer-saved')
        post_delete.connect(chatbot.clear_cache, sender=ChatAnswer, dispatch_uid='chat-answer-deleted')
