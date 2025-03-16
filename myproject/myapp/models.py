from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Links to Django's built-in User model

    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )
    RELATIONSHIP_CHOICES = (
        ('short_term', 'Short Term'),
        ('long_term', 'Long Term'),
        ('unsure', 'Still Trying to Figure Out'),
    )
    CITY_CHOICES = (
        ('adrian', 'Adrian'),
        ('hudson', 'Hudson'),
        ('toledo', 'Toledo'),
        ('jackson', 'Jackson'),
    )
    HOBBIES_CHOICES = (
        ('bowling', 'Bowling'),
        ('movies', 'Movies'),
        ('workout', 'Workout'),
        ('reading', 'Reading'),
        ('gaming', 'Gaming'),
        ('nature', 'Nature'),
    )

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES, blank=True, null=True)
    city = models.CharField(max_length=20, choices=CITY_CHOICES, blank=True, null=True)
    height = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True, help_text="Height in feet (e.g., 5.9)")
    hobbies = models.CharField(max_length=255, blank=True, null=True, help_text="Comma-separated hobbies (e.g., bowling,movies,reading)")

    def __str__(self):
        return self.user.username 
    
    def hobbies_list(self):
        if not self.hobbies:
         return []
        return [hobby.strip() for hobby in self.hobbies.split(',')]