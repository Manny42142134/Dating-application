from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileCreationForm(UserCreationForm):
    relationship_type = forms.ChoiceField(
        choices=UserProfile.RELATIONSHIP_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    city = forms.ChoiceField(
        choices=UserProfile.CITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    gender = forms.ChoiceField(
        choices=UserProfile.GENDER_CHOICES,
        required=False,
        widget=forms.RadioSelect
    )
    gender_preference = forms.ChoiceField(
        choices=UserProfile.GENDER_PREFERENCE_CHOICES,
        required=False,
        initial='both',
        widget=forms.RadioSelect
    )
    height = forms.DecimalField(
        max_digits=4,
        decimal_places=1,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    hobbies = forms.MultipleChoiceField(
        choices=UserProfile.HOBBIES_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    profile_pic = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'relationship_type',
                 'city', 'gender', 'gender_preference', 'height', 'hobbies', 'profile_pic')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            user_profile.relationship_type = self.cleaned_data['relationship_type']
            user_profile.city = self.cleaned_data['city']
            user_profile.gender = self.cleaned_data['gender']
            user_profile.gender_preference = self.cleaned_data['gender_preference']
            user_profile.height = self.cleaned_data['height']
            user_profile.hobbies = ','.join(self.cleaned_data['hobbies'])
            if self.cleaned_data.get('profile_pic'):
                user_profile.profile_pic = self.cleaned_data.get('profile_pic')
            user_profile.save()
        return user