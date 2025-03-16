from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileCreationForm(UserCreationForm):
    relationship_type = forms.ChoiceField(choices=UserProfile.RELATIONSHIP_CHOICES, required=False)
    city = forms.ChoiceField(choices=UserProfile.CITY_CHOICES, required=False)
    gender = forms.ChoiceField(choices=UserProfile.GENDER_CHOICES, required=False)
    height = forms.DecimalField(max_digits=4, decimal_places=1, required=False)
    hobbies = forms.CharField(max_length=255, required=False)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'relationship_type', 'city', 'gender', 'height', 'hobbies')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Check if a UserProfile already exists for this user
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            # Update the profile fields
            user_profile.relationship_type = self.cleaned_data['relationship_type']
            user_profile.city = self.cleaned_data['city']
            user_profile.gender = self.cleaned_data['gender']
            user_profile.height = self.cleaned_data['height']
            user_profile.hobbies = self.cleaned_data['hobbies']
            user_profile.save()
        return user
    



    