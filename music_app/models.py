import uuid
from django.db import models
from djongo import models as djongo_models

#todo make sure files / post can be deleted, but will be replaced by placeholders
#Why do I have sound / audio manager?
#Why do I have audio / sound model seperate?
class SoundManager(djongo_models.DjongoManager):
    pass

class Sound(models.Model):
    name = models.CharField(max_length=100)
    file_path = models.FileField(upload_to='audio_files/')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    tags = models.TextField(blank=True)  # You can use TextField to store a list of tags
    username = models.CharField(max_length=100)
    custom_file_name = models.CharField(max_length=255, blank=True)
    user_timestamp = models.DateTimeField()
    objects = SoundManager()
    class Meta:
        # Specify the database alias for this model
        # Use 'mongodb' to indicate that it should use the MongoDB database
        _use_db = 'mongodb'
        db_table = 'sound_file'

    def delete(self, *args, **kwargs):
        # Delete the associated file first
        if self.file_path:
            try:
                os.remove(self.file_path)
            except Exception as e:
                pass  # Handle the exception as needed

        # Call the parent's delete() method to remove the MongoDB document
        super(Sound, self).delete(*args, **kwargs)

from django.db import models
from smart_user_management.models import CustomUser  # Replace with your actual import
from django.db import models
import uuid
import os
from django.utils import timezone

class Tag(models.Model):
    tag_name = models.CharField(max_length=255)

class AudioManager(models.Manager):
    pass

class Audio(models.Model):
    audio_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    #Creater / owner:
    user_id_backend_audio = models.ForeignKey('smart_user_management.CustomUser', related_name='created_audios', on_delete=models.CASCADE)
    #User who reused the already posted file and post it again. Even if the user is deleted CASCADE will only delete the reposts
    reposted_by_user = models.ForeignKey('smart_user_management.CustomUser', related_name='reposted_audios', blank=True, null=True, on_delete=models.CASCADE)
    audio_title = models.CharField(max_length=100)
    audio_description = models.CharField(max_length=1000)
    #Created automatically:
    audio_link = models.FileField(upload_to='audio_files/')
    user_frontend_timestamp = models.DateTimeField(null=True, blank=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    duration = models.IntegerField(null=True, blank=True)
    duration_in_milliseconds = models.IntegerField(null=True, blank=True)  # New field for duration
    tags = models.ManyToManyField(Tag, through='AudioTag')
    objects = AudioManager()
    
    def delete(self, *args, **kwargs):
        if self.audio_link:
            try:
                os.remove(self.audio_link.path)
            except Exception as e:
                pass  # Handle the exception as needed
        super(Audio, self).delete(*args, **kwargs)

    def __str__(self):
            return f"AudioFile: {self.audio_title if self.audio_title else self.audio_uuid}"

    def to_dict(self):
        return {
            'audio_title': self.audio_title,
            'description': self.audio_description,
            'clientAppAudioFilePath': self.audio_link.url,
            'duration': self.duration,
            'durationMilliseconds': self.duration_in_milliseconds,
            #'frontend_id': self.user_id_backend_audio,
            #'tags': [tag.name for tag in self.tags.all()],
            'user': self.user_id_backend_audio.to_dict() if self.user_id_backend_audio else None,
            'customFileName': self.audio_title,
            'userTimeStamp': self.user_frontend_timestamp,
        }

from django.db import models

class PersonalGrowthCharacteristic(models.Model):
    category = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f"{self.category}; {self.name}; {self.description}"



class ExerciseType(models.Model):
    name = models.CharField(max_length=50, unique=True)  # Internal name
    display_name = models.CharField(max_length=100)  # User-friendly name
    description = models.TextField(blank=True, null=True)  # Optional metadata
    is_exclusive = models.BooleanField(default=False)  # Flag for subscription-based types
    priority = models.PositiveIntegerField(default=0)  # Lower numbers indicate higher priority
    is_active = models.BooleanField(default=True)  # For enabling/disabling types

    class Meta:
        ordering = ['priority']  # Automatically order by priority in queries

    def __str__(self):
        return self.display_name

class Exercise(models.Model):
    exercise_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='exercise_thumbnails/', blank=True, null=True)
    media = models.FileField(upload_to='exercise_media/', blank=True, null=True)
    instructions = models.TextField()
    duration = models.DurationField()
    xp = models.PositiveIntegerField()
    is_default = models.BooleanField(default=False)
    is_exclusive = models.BooleanField(default=False)
    exercise_type = models.ForeignKey(
        ExerciseType, related_name='exercises', on_delete=models.CASCADE
    )  # Dynamic relationship
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField('Tag', related_name='exercise_tags', blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        CustomUser, related_name='created_exercises', on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        return self.name

from django.db import models
from smart_user_management.models import CustomUser

class UserExercisePreference(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='exercise_preferences')
    exercise = models.ForeignKey('Exercise', on_delete=models.CASCADE, related_name='preferred_by_users')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'exercise')  # Prevent duplicates

    def __str__(self):
        return f"{self.user.username} -> {self.exercise.name}"


#The Post model is basically just a container for audio files or compositions
#If a Post gets rated not the actual Post object will receive the rating but the audio or composition
class Post(models.Model):
    post_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user_id_backend_post = models.ForeignKey(CustomUser, related_name='user_posts', on_delete=models.CASCADE)
    reposted_by_user = models.ForeignKey('smart_user_management.CustomUser', related_name='reposted_posts', blank=True, null=True, on_delete=models.CASCADE)    
    post_description = models.TextField()
    likers = models.ManyToManyField(CustomUser, related_name='liked_posts', blank=True)
    rating_average = models.FloatField(null=True, blank=True)
    audio_fk = models.ForeignKey('Audio', on_delete=models.SET_NULL, null=True, blank=True)
    composition_fk = models.ForeignKey('Composition', on_delete=models.SET_NULL, null=True, blank=True)
    video_fk = models.ForeignKey('Video', on_delete=models.SET_NULL, null=True, blank=True)  # New field for video
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, through='PostTag')

    @property
    def total_likes(self):
        return self.likers.count()

class PostTag(models.Model):
    post = models.ForeignKey(Post, related_name='tag_set', on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['post', 'tag']

class AudioTag(models.Model):
    audio = models.ForeignKey(Audio, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['audio', 'tag']

# Image model
class Image(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    image_file = models.ImageField(upload_to='image_files/', null=True, blank=True)  # Store image files
    created_at = models.DateTimeField(auto_now_add=True)

# Post_Image model
class PostImage(models.Model):
    user_id_backend_post_image = models.ForeignKey('smart_user_management.CustomUser', related_name='created_image',blank=True, null=True, on_delete=models.CASCADE)
    reposted_by_user = models.ForeignKey('smart_user_management.CustomUser', related_name='reposted_image', blank=True, null=True, on_delete=models.CASCADE)  
    post = models.ForeignKey(Post, related_name='image_set', on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)

# models.py
import uuid
from django.db import models
from smart_user_management.models import CustomUser

class Video(models.Model):
    video_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(CustomUser, related_name='user_videos', on_delete=models.CASCADE)
    video_title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='videos/')
    # Add other fields as needed

    def __str__(self):
        return self.video_title



from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class ContentTag(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    
    # Fields needed for the GenericForeignKey relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['tag', 'content_type', 'object_id']

# Favorite model
class Favorite(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

# Rating model
class Rating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    rating = models.IntegerField()

# Comment model
class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Composition model
# models.py

from django.db import models
import uuid

class Composition(models.Model):
    composition_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user_id_backend_composition = models.ForeignKey('smart_user_management.CustomUser', related_name='created_compositions', on_delete=models.CASCADE)
    reposted_by_user = models.ForeignKey('smart_user_management.CustomUser', related_name='reposted_compositions', blank=True, null=True, on_delete=models.CASCADE)    
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Assuming duration fields are integers representing milliseconds.
    duration = models.IntegerField(null=True, blank=True)  # Total duration
    duration_in_milliseconds = models.IntegerField(null=True, blank=True)  # Total duration in milliseconds
    mongo_db_id = models.CharField(max_length=200, blank=True, null=True)
    def __str__(self):
        return self.title

    def to_dict(self):
        return {
            'user': self.user_id_backend_composition.to_dict() if self.user_id_backend_composition else None,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'duration': self.duration,
            'durationMilliseconds': self.duration_in_milliseconds,
            'user_frontend_id': self.user_id_backend_composition.to_dict() if self.user_id_backend_composition else None,
            #'composition_tags': self.
            #'tags': tags,
        }
class CompositionAudio(models.Model):
    CONTENT_TYPE_CHOICES = (
    ('audio_file', 'Audio File'),
    ('composition', 'Composition'),
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    content_type = models.CharField(max_length=50, choices=CONTENT_TYPE_CHOICES)
    audio_file = models.ForeignKey(Audio, on_delete=models.SET_NULL, null=True, blank=True)
    composition = models.ForeignKey(
        Composition, 
        related_name='composition_audios', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    audio_position = models.IntegerField(default=0)
    audio_repetition = models.IntegerField(default=1)
    def __str__(self):
        return f"CompositionAudio: {self.uuid}"
    def to_dict(self):
        return {
            'composition_audio_id': self.uuid,
            'content_type': self.content_type,
            #'composition_tags': self.
            #'tags': tags,
            'audio_position' : self.audio_position,
            'audio_repetition' : self.audio_repetition,
        }


from django.db import models

class CompositionTag(models.Model):
    composition = models.ForeignKey(Composition, on_delete=models.CASCADE)
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['composition', 'tag']

    def __str__(self):
        return f"{self.composition.title} - Tag: {self.tag.tag_name}"


# TagRating model
class TagRating(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    content_id = models.IntegerField()
    content_type = models.CharField(max_length=50)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Event model
class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

# Transaction model
class Transaction(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=255)
    amount = models.FloatField()
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

# Subscription model
class Subscription(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

# Product model
class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Bug_and_Enhancement_Report model
class BugAndEnhancementReport(models.Model):
    user = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=50)
    severity = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    feedback = models.TextField()

