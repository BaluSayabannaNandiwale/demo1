"""
Django forms for accounts app.
Converted from Flask-WTF forms.
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import User


class RegisterForm(forms.Form):
    """User registration form"""
    name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'John Doe'
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'example@company.com'
    }))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))
    user_type = forms.ChoiceField(
        choices=[('student', 'Student'), ('teacher', 'Professor')],
        required=True,
        widget=forms.Select(attrs={'class': 'custom-select my-1 mr-sm-2'})
    )
    image_hidden = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered. Please use a different email or login.")
        return email
    
    def clean_image_hidden(self):
        """Accept empty image; view will use placeholder when creating user if needed."""
        imgdata = (self.cleaned_data.get('image_hidden') or '').strip()
        if not imgdata or len(imgdata) < 100:
            # Placeholder so User model accepts it; user can add photo later if needed
            return ''
        return imgdata


class LoginForm(forms.Form):
    """User login form (image_hidden optional when face verification unavailable)."""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email address'
    }))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))
    user_type = forms.ChoiceField(
        choices=[('student', 'Student'), ('teacher', 'Professor')],
        required=True,
        widget=forms.Select(attrs={'class': 'custom-select my-1 mr-sm-2'})
    )
    image_hidden = forms.CharField(widget=forms.HiddenInput(), required=False)


class ChangePasswordForm(forms.Form):
    """Change password form (oldpassword, newpassword; confirmpassword optional for templates that omit it)."""
    oldpassword = forms.CharField(required=True, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Old password'
    }))
    newpassword = forms.CharField(required=True, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'New password'
    }))
    confirmpassword = forms.CharField(required=False, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Confirm new password'
    }))
    
    def clean(self):
        cleaned_data = super().clean()
        newpassword = cleaned_data.get('newpassword')
        confirmpassword = cleaned_data.get('confirmpassword')
        if newpassword and confirmpassword and newpassword != confirmpassword:
            raise ValidationError("Passwords don't match.")
        return cleaned_data


class LostPasswordForm(forms.Form):
    """Lost password form"""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email address'
    }))


class NewPasswordForm(forms.Form):
    """New password form after OTP verification (forgot password flow)."""
    npwd = forms.CharField(required=True, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'New password'
    }))
    cpwd = forms.CharField(required=True, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Confirm password'
    }))
    
    def clean(self):
        cleaned_data = super().clean()
        npwd = cleaned_data.get('npwd')
        cpwd = cleaned_data.get('cpwd')
        if npwd and cpwd and npwd != cpwd:
            raise ValidationError("Passwords don't match.")
        return cleaned_data
class ContactForm(forms.Form):
    """Contact form (cname, cemail, cquery) to match contact.html."""
    cname = forms.CharField(required=True, max_length=200, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'EG. John David'
    }))
    cemail = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'example@company.com'
    }))
    cquery = forms.CharField(required=True, widget=forms.Textarea(attrs={
        'class': 'form-control', 'placeholder': 'How can we help?', 'rows': 4
    }))