from django import forms
from .models import Entry

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['memory_title', 'content', 'mood']
        widgets = {
            'memory_title': forms.Textarea(attrs={
                'rows': 2, 'class': 'resize-none rounded w-full p-2'
            }),
            'content': forms.Textarea(attrs={
                'rows': 6, 'class': 'resize-none rounded w-full p-2'
            }),
            'mood': forms.Select(attrs={
                'class': 'rounded w-full p-2 border border-gray-300'
            }),
        }
