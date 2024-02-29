# forms.py
from django import forms
from django.contrib.auth.models import User
from store.models import Store

class StoreRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Store
        fields = ['name', 'address']  # Add other fields from Store model as needed

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        store = super().save(commit=False)
        store.user = user
        if commit:
            store.save()
        return store
