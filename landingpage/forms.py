from django.contrib.auth.models import User
from django import forms


class UserForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Enter username", "class": "form-control"}
        ),
        min_length=4,
        max_length=150,
        required=True,
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Enter password", "class": "form-control"}
        ),
        min_length=8,
        max_length=20,
        required=True,
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"placeholder": "Enter email", "class": "form-control"}
        ),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]


class LoginForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Enter username", "class": "form-control"}
        ),
        min_length=4,
        max_length=150,
        required=True,
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Enter password", "class": "form-control"}
        ),
        required=True,
    )

    class Meta:
        model = User
        fields = ["username", "password"]


class validateionCodeForm(forms.Form):
    validition = forms.IntegerField(
        widget=forms.TextInput(
            attrs={"placeholder": "Enter validation code", "class": "form-control"}
        )
    )
