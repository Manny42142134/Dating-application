from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import UserProfileCreationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile, Swipe, Match, Message
from django.db.models import Q
import json
import random
import requests 
from django.templatetags.static import static
from django.contrib.auth import logout

def register_page(request):
    if request.method == 'POST':
        form = UserProfileCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('user')
        else:
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
            return redirect('user')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def products(request):
    return render(request, 'product.html')

def user(request):
    if request.method == 'POST':
        print(request.POST)  # Debugging
        user_profile = request.user.userprofile

        # Process form data
        user_profile.relationship_type = request.POST.get('relationship_type')
        user_profile.city = request.POST.get('city')
        user_profile.gender = request.POST.get('gender')
        
        # Add gender preference processing
        user_profile.gender_preference = request.POST.get('gender_preference', 'both')
        
        # Process height
        feet = request.POST.get('feet', 0)
        inches = request.POST.get('inches', 0)
        try:
            user_profile.height = float(feet) + float(inches) / 12.0
        except (TypeError, ValueError):
            user_profile.height = None
        
        # Process hobbies
        hobbies = request.POST.getlist('hobbies', [])
        user_profile.hobbies = ','.join(hobbies) if hobbies else ''
        
        # Process profile picture if needed
        if 'profile_pic' in request.FILES:
            user_profile.profile_pic = request.FILES['profile_pic']
        
        user_profile.save()
        return redirect('date')  # Redirect to date page
        
    return render(request, 'user.html')

def update(request):
    if request.method == 'POST':
        print(request.POST)
        user_profile = request.user.userprofile

        user_profile.relationship_type = request.POST.get('relationship_type')
        user_profile.city = request.POST.get('city')
        user_profile.gender = request.POST.get('gender')
        
        # Add gender preference processing
        user_profile.gender_preference = request.POST.get('gender_preference', 'both')
        
        feet = request.POST.get('feet')
        inches = request.POST.get('inches')
        if feet and inches:
            user_profile.height = float(feet) + float(inches) / 12.0
        
        hobbies = request.POST.getlist('hobbies')
        user_profile.hobbies = ','.join(hobbies)
        
        # Process profile picture update if provided
        if 'profile_pic' in request.FILES:
            user_profile.profile_pic = request.FILES['profile_pic']

        user_profile.save()
        return redirect('user')
    else:
        # Render update form with existing profile information
        user_profile = request.user.userprofile
        context = {
            'profile': user_profile,
            'current_gender_preference': user_profile.gender_preference
        }
        return render(request, 'update.html', context)


def date_page(request):
    user_profile = request.user.userprofile
    
    height_feet = int(user_profile.height) if user_profile.height else 0
    height_inches = int((user_profile.height - height_feet) * 12) if user_profile.height else 0
    
    context = {
        'username': request.user.username,
        'email': request.user.email,
        'relationship_type': user_profile.get_relationship_type_display(),
        'city': user_profile.get_city_display(),
        'gender': user_profile.get_gender_display(),
        'gender_preference': user_profile.get_gender_preference_display(),
        'height': f"{height_feet} ft {height_inches} in" if user_profile.height else "Not specified",
        'hobbies': user_profile.hobbies_list(),
    }
    
    return render(request, 'date.html', context)

def logout_view(request):
    logout(request)  # Ends the user session
    return redirect('register')  # Redirect to the register view after logout

def get_profiles(request):
    user_profile = request.user.userprofile
    potential_matches = user_profile.get_potential_matches()
    
    # Define two groups of dummy images
    profile_images = [
        static('images/profile1.jpg'),
        static('images/profile2.jpg'),
        static('images/profile3.jpg'),
        static('images/profile4.jpg'),
        static('images/profile5.jpg'),
        static('images/profile6.jpg'),
        static('images/profile7.jpg'),
        static('images/profile8.jpg'),
    ]
    mprofile_images = [
        static('images/mprofile1.jpg'),
        static('images/mprofile2.jpg'),
        static('images/mprofile3.jpg'),
        static('images/mprofile4.jpg'),
        static('images/mprofile5.jpg'),
        static('images/mprofile6.jpg'),
    ]
    
    # Shuffle each group separately for randomization within each group
    random.shuffle(profile_images)
    random.shuffle(mprofile_images)
    
    profiles_data = []
    
    female_count = 0
    male_count = 0
    
    for profile in potential_matches:
        # Format height if available
        if profile.height:
            height_feet = int(profile.height)
            height_inches = int((profile.height - height_feet) * 12)
            height_text = f"{height_feet} ft {height_inches} in"
        else:
            height_text = "Not specified"
        
        # Use gender to determine which image set to use
        if profile.gender == 'female':
            index = female_count % len(profile_images)
            image_url = profile_images[index]
            bio = generate_random_bio("female", profile.hobbies_list() or [])
            female_count += 1
        else:  # male or other
            index = male_count % len(mprofile_images)
            image_url = mprofile_images[index]
            bio = generate_random_bio("male", profile.hobbies_list() or [])
            male_count += 1
            
        # Calculate hobby match score
        hobby_match_score = user_profile.calculate_hobby_match_score(profile)
        
        profiles_data.append({
            'id': profile.id,
            'name': profile.user.username,
            'location': profile.get_city_display(),
            'hobbies': profile.hobbies_list(),
            'image': image_url,
            'height': height_text,
            'bio': bio,
            'hobby_match_score': hobby_match_score,
            'hobby_match_percentage': int((hobby_match_score / max(len(user_profile.hobbies_list()), 1)) * 100) if user_profile.hobbies_list() else 0,
        })
    
    return JsonResponse(profiles_data, safe=False)

@csrf_exempt
def handle_swipe(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Get and validate profile_id
            raw_profile_id = data.get('profile_id')
            if raw_profile_id is None:
                return JsonResponse({'status': 'error', 'message': 'Missing profile_id'}, status=400)
            try:
                swiped_profile_id = int(raw_profile_id)
            except ValueError:
                return JsonResponse({'status': 'error', 'message': 'Invalid profile_id'}, status=400)
    
            # Get the action.
            action = data.get('action')
            if not action:
                return JsonResponse({'status': 'error', 'message': 'Missing action'}, status=400)
    
            # Determine if this swipe is for a dummy (is_mock)
            is_mock = data.get('is_mock', False)
    
            # Get the swiper's profile.
            swiper_profile = request.user.userprofile
            
            if is_mock:
                # For dummy profiles, calculate match based on provided hobbies.
                dummy_hobbies = data.get('hobbies', [])
                normalized_dummy = {h.strip().lower() for h in dummy_hobbies}
                normalized_user = {h.strip().lower() for h in swiper_profile.hobbies_list()}
                hobby_match_score = len(normalized_dummy & normalized_user)
                if action == 'like' and hobby_match_score >= 1:
                    # Return a match response without storing in the DB.
                    return JsonResponse({
                        'status': 'match',
                        'is_mock': True,
                        'hobby_match_score': hobby_match_score,
                        'match_percentage': int((hobby_match_score / max(len(normalized_user), 1)) * 100)
                    })
                return JsonResponse({'status': 'success'})
    
            # For real profiles:
            try:
                swiped_profile = UserProfile.objects.get(id=swiped_profile_id)
            except UserProfile.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Profile not found'}, status=400)
    
            # Record the swipe (using get_or_create to avoid duplicates)
            swipe, created = Swipe.objects.get_or_create(
                swiper=swiper_profile,
                swiped_on=swiped_profile,
                defaults={'action': action}
            )
            if not created:
                swipe.action = action
                swipe.save()
    
            if action == 'like':
                # Check for reciprocal like.
                reciprocal_like = Swipe.objects.filter(
                    swiper=swiped_profile,
                    swiped_on=swiper_profile,
                    action='like'
                ).exists()
                if reciprocal_like:
                    match_exists = Match.objects.filter(
                        Q(user1=swiper_profile, user2=swiped_profile) | Q(user1=swiped_profile, user2=swiper_profile)
                    ).exists()
                    if not match_exists:
                        hobby_match_score = swiper_profile.calculate_hobby_match_score(swiped_profile)
                        if hobby_match_score >= 1:
                            Match.objects.create(
                                user1=swiper_profile,
                                user2=swiped_profile,
                                hobby_match_score=hobby_match_score
                            )
                            return JsonResponse({
                                'status': 'match',
                                'hobby_match_score': hobby_match_score,
                                'match_percentage': int((hobby_match_score / max(len(swiper_profile.hobbies_list()), 1)) * 100)
                            })
            return JsonResponse({'status': 'success'})
    
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=400)


def get_matches(request):
    user_profile = request.user.userprofile
    matches = Match.objects.filter(
        Q(user1=user_profile) | Q(user2=user_profile)
    )
    matches_data = []
    for match in matches:
        # Determine the other user in the match.
        other_user = match.user1 if match.user2 == user_profile else match.user2
        matches_data.append({
            'id': other_user.id,
            'name': other_user.user.username,
            'image': other_user.profile_pic.url if other_user.profile_pic else None,
            'hobby_match_score': match.hobby_match_score,
            'match_percentage': int((match.hobby_match_score / max(len(user_profile.hobbies_list()), 1)) * 100) if user_profile.hobbies_list() else 0
        })
    
    return JsonResponse(matches_data, safe=False)

@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            sender = request.user  # Assuming the user is authenticated.
            receiver_id = data.get('receiver_id')
            content = data.get('content')
            if not receiver_id or not content:
                return JsonResponse({'status': 'error', 'message': 'Missing data'}, status=400)
           
            from django.contrib.auth import get_user_model
            User = get_user_model()
            receiver = User.objects.get(id=receiver_id)
            message = Message.objects.create(sender=sender, receiver=receiver, content=content)
            return JsonResponse({'status': 'success', 'message': 'Message sent'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@csrf_exempt
def get_messages(request):
    if request.method == 'GET':
        user = request.user
        # Retrieve all messages where the user is sender or receiver.
        messages = Message.objects.filter(sender=user) | Message.objects.filter(receiver=user)
        messages = messages.order_by('timestamp')
        messages_list = []
        for msg in messages:
            messages_list.append({
                'id': msg.id,
                'sender': msg.sender.username,
                'receiver': msg.receiver.username,
                'content': msg.content,
                'timestamp': msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            })
        return JsonResponse(messages_list, safe=False)
    return JsonResponse({'status': 'error', 'message': 'GET request required'}, status=400)

def generate_random_bio(gender, hobbies):
    """Generate a bio in one sentence: 'He likes X, and he also likes Y.'"""
    # Use defaults if no hobbies are provided
    if not hobbies:
        hobbies = [
            'bowling', 'movies', 'workout', 'reading', 'gaming',
            'nature', 'cooking', 'traveling', 'photography', 'dancing',
            'music', 'sports', 'art', 'fishing', 'cycling'
        ]
    
    # Randomly select three hobbies
    hobby_pair = random.sample(hobbies, k=min(3, len(hobbies)))
    while len(hobby_pair) < 3:
        random_hobby = random.choice(hobbies)
        if random_hobby not in hobby_pair:
            hobby_pair.append(random_hobby)
    
    # Choose pronouns based on gender
    if gender == 'male':
        pronoun = "He"
        pronoun_lower = "he"
    elif gender == 'female':
        pronoun = "She"
        pronoun_lower = "she"
    else:
        pronoun = "They"
        pronoun_lower = "they"
    
    return f"{pronoun} likes {hobby_pair[0]}, and {pronoun_lower} also likes {hobby_pair[1]}, and likes {hobby_pair[2]}."
    
@csrf_exempt
def fetch_dummy_users(request):
    """
    Generate dummy user data using local images.
    Returns formatted user data including:
      - Dummy name, age, gender, location
      - Profile image that matches gender (male for mprofile*, female for profile*)
      - Random hobbies from a predefined list
      - Random height and a generated bio with correct pronouns
      - Random relationship_type chosen from 'short_term', 'long_term', or 'unsure'
    """
    HOBBY_CHOICES = [
        'bowling', 'movies', 'workout', 'reading', 'gaming',
        'nature', 'cooking', 'traveling', 'photography', 'dancing',
        'music', 'sports', 'art', 'fishing', 'cycling'
    ]
    
    # Define relationship choices
    RELATIONSHIP_CHOICES = ['short-term', 'long-term', 'unsure']
    
    # Separate profile images by gender prefix
    MALE_IMAGES = [
        'mprofile1.jpg', 'mprofile2.jpg', 'mprofile3.jpg',
        'mprofile4.jpg', 'mprofile5.jpg', 'mprofile6.jpg'
    ]
    
    FEMALE_IMAGES = [
        'profile1.jpg', 'profile2.jpg', 'profile3.jpg', 'profile4.jpg',
        'profile5.jpg', 'profile6.jpg', 'profile7.jpg', 'profile8.jpg'
    ]
    
    # Get user's gender preference from request
    user_profile = request.user.userprofile
    gender_preference = user_profile.gender_preference
    
    formatted_users = []
    
    # For male dummy profiles
    if gender_preference in ['male', 'both']:
        for idx, image in enumerate(MALE_IMAGES):
            feet = random.randint(5, 6)
            inches = random.randint(0, 11)
            hobby_sample = random.sample(HOBBY_CHOICES, k=3)
            
            dummy_name = f"Male User {idx + 1}"
            dummy_age = random.randint(20, 28)
            dummy_location = "Sample City, Sample Country"
            
            # Randomly assign relationship type
            relationship_type = random.choice(RELATIONSHIP_CHOICES)
            
            bio = generate_random_bio('male', hobby_sample)
            image_url = static('images/' + image)
            
            formatted_users.append({
                'id': 1000 + idx,  # Use IDs that won't conflict
                'name': dummy_name,
                'age': dummy_age,
                'image': image_url,
                'location': dummy_location,
                'gender': 'male',
                'hobbies': hobby_sample,
                'height': f"{feet}.{inches:02d}",
                'bio': bio,
                'relationship_type': relationship_type,
                'hobby_match_score': len(set(hobby_sample) & set(user_profile.hobbies_list()))
            })
    
    # For female dummy profiles
    if gender_preference in ['female', 'both']:
        for idx, image in enumerate(FEMALE_IMAGES):
            feet = random.randint(4, 5)
            inches = random.randint(0, 11)
            hobby_sample = random.sample(HOBBY_CHOICES, k=3)
            
            dummy_name = f"Female User {idx + 1}"
            dummy_age = random.randint(20, 30)
            dummy_location = "Sample City, Sample Country"
            
            # Randomly assign relationship type
            relationship_type = random.choice(RELATIONSHIP_CHOICES)
            
            bio = generate_random_bio('female', hobby_sample)
            image_url = static('images/' + image)
            
            formatted_users.append({
                'id': 2000 + idx,  # Use IDs that won't conflict
                'name': dummy_name,
                'age': dummy_age,
                'image': image_url,
                'location': dummy_location,
                'gender': 'female',
                'hobbies': hobby_sample,
                'height': f"{feet}.{inches:02d}",
                'bio': bio,
                'relationship_type': relationship_type,
                'hobby_match_score': len(set(hobby_sample) & set(user_profile.hobbies_list()))
            })
    
    # Shuffle the combined list for random order and return
    random.shuffle(formatted_users)
    return JsonResponse(formatted_users, safe=False)
