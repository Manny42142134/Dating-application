# Add gender preference field to UserProfile model
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    GENDER_PREFERENCE_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('both', 'Both'),
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
        ('detroit', 'Detroit'),
        ('grand_rapids', 'Grand Rapids'),
        ('ann_arbor', 'Ann Arbor'),
        ('lansing', 'Lansing'),
        ('flint', 'Flint'),
        ('kalamazoo', 'Kalamazoo'),
        ('saginaw', 'Saginaw'),
        ('traverse_city', 'Traverse City'),
        ('muskegon', 'Muskegon'),
        ('port_huron', 'Port Huron'),
    )
    HOBBIES_CHOICES = (
        ('bowling', 'Bowling'),
        ('movies', 'Movies'),
        ('workout', 'Workout'),
        ('reading', 'Reading'),
        ('gaming', 'Gaming'),
        ('nature', 'Nature'),
        ('cooking', 'Cooking'),
        ('traveling', 'Traveling'),
        ('photography', 'Photography'),
        ('dancing', 'Dancing'),
        ('music', 'Music'),
        ('sports', 'Sports'),
        ('art', 'Art'),
        ('fishing', 'Fishing'),
        ('cycling', 'Cycling'),
    )

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    gender_preference = models.CharField(max_length=10, choices=GENDER_PREFERENCE_CHOICES, default='both')
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES, blank=True, null=True)
    city = models.CharField(max_length=20, choices=CITY_CHOICES, blank=True, null=True)
    height = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    hobbies = models.CharField(max_length=255, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username
    
    def hobbies_list(self):
        if not self.hobbies:
            return []
        return [hobby.strip() for hobby in self.hobbies.split(',')]

    def get_potential_matches(self):
        """Get profiles that haven't been swiped on yet and match gender preference"""
        swiped_profiles = self.swipes_made.values_list('swiped_on__id', flat=True)
        
        # Base query to exclude already swiped profiles and self
        base_query = Q(id__in=swiped_profiles) | Q(user=self.user)
        
        # Apply gender preference filter
        gender_filter = Q()
        if self.gender_preference == 'male':
            gender_filter = Q(gender='male')
        elif self.gender_preference == 'female':
            gender_filter = Q(gender='female')
        # If 'both', no additional filter needed
        
        return UserProfile.objects.exclude(base_query).filter(gender_filter)
    
    def calculate_hobby_match_score(self, other_profile):
        """Calculate how many hobbies match between two profiles"""
        if not self.hobbies or not other_profile.hobbies:
            return 0
            
        self_hobbies = set(self.hobbies_list())
        other_hobbies = set(other_profile.hobbies_list())
        
        return len(self_hobbies.intersection(other_hobbies))

class Swipe(models.Model):
    """Model to track swipes between users"""
    swiper = models.ForeignKey(
        UserProfile, 
        related_name='swipes_made',
        on_delete=models.CASCADE
    )
    swiped_on = models.ForeignKey(
        UserProfile, 
        related_name='swipes_received',
        on_delete=models.CASCADE
    )
    action = models.CharField(
        max_length=10,
        choices=(('like', 'Like'), ('pass', 'Pass'))
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('swiper', 'swiped_on')

    def __str__(self):
        return f"{self.swiper} -> {self.swiped_on}: {self.action}"

class Match(models.Model):
    """Model to track mutual likes (matches)"""
    user1 = models.ForeignKey(
        UserProfile, 
        related_name='matches_as_user1',
        on_delete=models.CASCADE
    )
    user2 = models.ForeignKey(
        UserProfile, 
        related_name='matches_as_user2',
        on_delete=models.CASCADE
    )
    # Store hobby match score
    hobby_match_score = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"Match between {self.user1} and {self.user2}"
    
    User = get_user_model()

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username} at {self.timestamp}"