import datetime

from .models import BookInstance, Profile

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class AuthenticationForm(AuthenticationForm):
    username= forms.CharField(widget = forms.TextInput(attrs={
        'class': 'form-control'
    }))
    password = forms.CharField(widget= forms.PasswordInput(attrs={
        'class' : 'form-control'
    }))


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'favorite_Genre', 'profile_picture']


class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(help_text='Enter a date between now and 4 weeks (default 3)')

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        # check if date is not in the past

        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        return data


# class RenewBookForm1(forms.ModelForm):
#     class Meta:
#         model = BookInstance
#         fields = ['due_date']
#         labels = {
#             'due_date': _('Renewal Date')
#         }
#         help_texts = {
#             'due_date': _('Enter a date b\w now and 4 weeks.')
#         }
#
#     def clean_due_date(self):
#         data = self.cleaned_data['due_date']
#
#         # check if date is not in the past
#
#         if data < datetime.date.today():
#             raise ValidationError(_('Invalid date - renewal in past'))
#
#         if data > datetime.date.today() + datetime.timedelta(weeks=4):
#             raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))
#
#         return data

class IssueBookForm(forms.Form):
    class Meta:
        model = BookInstance
        fields = ['due_date', 'borrower', 'status']


class SignUpForm(UserCreationForm):
    location = forms.CharField(max_length=40, required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password1', 'password2',)



