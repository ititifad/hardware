# views.py
from django.shortcuts import render, redirect
from .forms import StoreRegistrationForm

def store_registration(request):
    if request.method == 'POST':
        form = StoreRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login page after successful registration
    else:
        form = StoreRegistrationForm()
    return render(request, 'users/store_registration.html', {'form': form})
