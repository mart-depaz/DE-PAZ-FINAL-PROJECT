# for accounts app
# accounts/forms.py


from django import forms
from .models import User
from django.forms.widgets import DateInput

class SignUpForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('full_name', 'email', 'birthdate', 'age', 'gender', 
                 'address', 'contact_no', 'is_pwd', 
                 'is_4ps_member', 'is_senior_citizen', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gender'].choices = User.GENDER_CHOICES
        self.fields['role'].choices = User.ROLE_CHOICES

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if role not in dict(User.ROLE_CHOICES).keys():
            raise forms.ValidationError("Invalid role selected.")
        return role

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('full_name', 'email', 'birthdate', 'age', 'gender', 
                 'address', 'contact_no', 'is_pwd', 
                 'is_4ps_member', 'is_senior_citizen')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gender'].choices = User.GENDER_CHOICES
        self.fields['birthdate'].widget = DateInput(attrs={'type': 'date'})

    def clean_contact_no(self):
        contact_no = self.cleaned_data.get('contact_no')
        if contact_no and not contact_no.isdigit():
            raise forms.ValidationError("Contact number should contain only digits.")
        if contact_no and len(contact_no) != 11:
            raise forms.ValidationError("Contact number should be 11 digits.")
        return contact_no

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

class CreatePasswordForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password", required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password", required=True)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        if len(password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        return cleaned_data