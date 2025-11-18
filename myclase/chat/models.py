from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.pk}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        null=True,      # <- si ya no lo necesitás, luego podés quitar null/blank
        blank=True,
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    text = models.TextField(blank=True)
    attachment = models.FileField(
        upload_to='chat_attachments/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # 👇 NUEVO: para saber si el receptor ya lo leyó
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Msg {self.pk} by {self.sender}"
