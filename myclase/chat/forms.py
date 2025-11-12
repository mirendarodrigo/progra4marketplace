from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text', 'attachment']
        widgets = {
            'text': forms.Textarea(attrs={'rows':2, 'placeholder':'Escribí tu mensaje...'})
        }
