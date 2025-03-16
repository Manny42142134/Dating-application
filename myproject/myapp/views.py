from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import UserProfileCreationForm

def register_page(request):
    if request.method == 'POST':
        form = UserProfileCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('user')  # Redirect to the user page (user.html)
        else:
            # Optionally, print or log form errors for debugging
            print(form.errors)
    else:
        form = UserProfileCreationForm()
    return render(request, 'register.html', {'form': form})

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('user')  # Make sure 'user' is a valid url name
        else:
            # If authentication fails, show the login page again with an error
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def products(request):
    return render(request, 'product.html')

def user(request):
    if request.method == 'POST':
        # Process hobbies (multiple checkboxes)
        hobbies = request.POST.getlist('hobbies')
        request.user.userprofile.hobbies = ','.join(hobbies)
        
        # Process other form fields if needed
        # Example: request.user.userprofile.relationship_type = request.POST.get('relationship_type')
        
        # Save the profile
        request.user.userprofile.save()
        return redirect('user')
        
    return render(request, 'user.html')

def update(request):
    if request.method == 'POST':
        # Process hobbies (multiple checkboxes)
        hobbies = request.POST.getlist('hobbies')
        request.user.userprofile.hobbies = ','.join(hobbies)
        
        # Process other form fields if needed
        # Example: request.user.userprofile.relationship_type = request.POST.get('relationship_type')
        
        # Save the profile
        request.user.userprofile.save()
        return redirect('user')
        
    return render(request, 'update.html')



def update(request):
    if request.method == 'POST':
        # Get the current user's profile
        user_profile = request.user.userprofile

        # Update the profile fields
        user_profile.relationship_type = request.POST.get('relationship_type')
        user_profile.city = request.POST.get('city')
        user_profile.gender = request.POST.get('gender')
        user_profile.height = request.POST.get('height')
        user_profile.hobbies = request.POST.get('hobbies')

        # Save the updated profile
        user_profile.save()

        # Redirect to the user page
        return redirect('user')
    else:
        # Render the update form
        return render(request, 'update.html')

