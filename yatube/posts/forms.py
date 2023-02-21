from django.forms import ModelForm
from django import forms

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': ('Текст'),
            'group': ('Группа'),
        }
        help_texts = {
            'text': ('Напишите же что-нибудь'),
            'group': ('Выберите группу'),
        }

#       Памятка как извещать об ошибках
#        error_messages = {
#            'text': {
#                'max_length': _("Длинноватое название!"),
#            },
#        }


class CommentForm(forms.ModelForm):
    class Meta():
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Текст комментария',
        }
        help_texts = {
            'text': 'Напишите ваш комментарий',
        }
