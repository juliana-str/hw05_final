from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Comment, Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': _('Текст поста'),
            'group': _('Группа')
        }
        help_texts = {
            'text': _('Напишите свой пост'),
            'group': _('Выбирете группу')
        }
        error_messages = {
            'text': {'max_length': _('Этот пост слишком длинный')},
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment

        fields = ('text',)
        labels = {
            'text': _('Текст комментария'),
        }
        help_texts = {
            'text': _('Напишите свой комментарий'),
        }
        error_messages = {
            'text': {'max_length':
                     _('Этот комментарий слишком длинный')},
        }
