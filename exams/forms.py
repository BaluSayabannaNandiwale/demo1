"""
Django forms for exams app.
"""
from django import forms


class GiveTestForm(forms.Form):
    """Exam login form: test_id, password, optional face image."""
    test_id = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Test ID',
            'id': 'id_test_id',
        }),
        label='Test ID',
    )
    password = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Test Password',
            'id': 'id_password',
        }),
        label='Password',
    )
    img_hidden_form = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'img_hidden'}),
        required=False,
    )
