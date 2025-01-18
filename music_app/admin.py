
from django.contrib import admin
from .models import  Audio, Transaction, Subscription
from .models import Post, Tag, ContentTag, Audio, Favorite, Rating, Comment, Event, Composition, CompositionAudio, Transaction, Subscription, Product, BugAndEnhancementReport, Image, PostImage, TagRating, PersonalGrowthCharacteristic, Video, Exercise,ExerciseType,UserExercisePreference

#Audios
class AudioAdmin(admin.ModelAdmin):
    list_display = ('id','audio_uuid','audio_title', 'user_id_backend_audio', 'audio_description',  'audio_link', 'user_frontend_timestamp','posted_at','updated_at','duration','duration_in_milliseconds')
    readonly_fields = ('posted_at','updated_at','audio_uuid', 'user_frontend_timestamp')
    search_fields = ['audio_title', 'user_id_backend__username']
    using = 'mongodb'

class PostAdmin(admin.ModelAdmin):
    list_display = ('post_uuid', 'user_id_backend_post','reposted_by_user', 'post_description', 'rating_average', 'created_at', 'updated_at', 'audio_fk', 'composition_fk','video_fk')
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ['post_description', 'user_id_backend_post__username']

    # If using a different database for Post model, specify using attribute
    # using = 'default'  # or name of your database


class CompositionAdmin(admin.ModelAdmin):
    list_display = ('id','composition_uuid', 'user_id_backend_composition', 'reposted_by_user', 'title', 'created_at', 'updated_at', 'duration', 'duration_in_milliseconds')
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ['title', 'user_id_backend_composition__username']

admin.site.register(Composition, CompositionAdmin)
from django.utils.html import format_html
from django.urls import reverse
class CompositionAudioAdmin(admin.ModelAdmin):
    list_display = ('id','uuid','get_audio_entry', 'get_audio_link', 'content_type', 'audio_file', 'composition', 'audio_position', 'audio_repetition')
    search_fields = ['composition__title', 'audio_file__audio_title']
    def get_audio_link(self, obj):
        if obj.audio_file and obj.audio_file.audio_link:
            return format_html("<a href='{url}'>AudioFile: {title}</a>", url=obj.audio_file.audio_link.url, title=obj.audio_file.audio_title or obj.audio_file.audio_uuid)
        else:
            return "No Audio"
    get_audio_link.short_description = 'Audio File'
    def get_audio_entry(self, obj):
        if obj.audio_file:
            # Get the admin URL for the audio instance
            audio_admin_url = reverse("admin:music_app_audio_change", args=[obj.audio_file.pk])  # make sure 'appname' is your actual app name
            # Return a clickable link to the admin edit page for the audio instance
            return format_html("<a href='{url}'>AudioFile: {title}</a>", url=audio_admin_url, title=obj.audio_file.audio_title or obj.audio_file.audio_uuid)
        else:
            return "No Audio"
    get_audio_link.short_description = 'Audio File'

admin.site.register(CompositionAudio, CompositionAudioAdmin)

class PersonalGrowthCharacteristicAdmin(admin.ModelAdmin):
    list_display = ('category', 'name', 'description')  # specify the fields to display


# ExerciseType Admin
class ExerciseTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_name', 'priority', 'is_exclusive', 'is_active')  # Columns in the admin view
    list_editable = ('priority', 'is_exclusive', 'is_active')  # Allow inline editing of these fields
    ordering = ['priority']  # Order by priority in the admin view
    search_fields = ['name', 'display_name']  # Enable search by name and display_name

# Exercise Admin
class ExerciseAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'exercise_uuid', 'exercise_type', 'is_default', 'is_exclusive',
        'duration', 'xp', 'created_at', 'updated_at', 'created_by'
    )  # Fields to display
    readonly_fields = ('exercise_uuid', 'created_at', 'updated_at')  # Non-editable fields
    search_fields = ['name', 'description', 'exercise_type__name', 'created_by__username']  # Enable search
    list_filter = ('is_default', 'is_exclusive', 'exercise_type')  # Filter options in the sidebar
    ordering = ['-created_at']  # Default ordering by most recent
    list_editable = ('duration',)  # Fields editable in the list view
    def tags_list(self, obj):
        """Display tags as a comma-separated list."""
        return ", ".join([tag.name for tag in obj.tags.all()])
    tags_list.short_description = "Tags"

# UserExercisePreference Admin
class UserExercisePreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'exercise', 'added_at')  # Fields to display
    search_fields = ['user__username', 'exercise__name']  # Enable search
    readonly_fields = ('added_at',)  # Make added_at non-editable
    list_filter = ('user', 'exercise')  # Filter options in the sidebar
    ordering = ['-added_at']  # Default ordering by most recent

# Register your models here

admin.site.register(Audio, AudioAdmin)
admin.site.register(Post, PostAdmin)
# Register the model for each table in the `music_app`
admin.site.register(PersonalGrowthCharacteristic, PersonalGrowthCharacteristicAdmin)
admin.site.register(Tag)
admin.site.register(ContentTag)
admin.site.register(Favorite)
admin.site.register(Rating)
admin.site.register(Comment)
admin.site.register(Event)
admin.site.register(Transaction)
admin.site.register(Subscription)
admin.site.register(Product)
admin.site.register(BugAndEnhancementReport)
admin.site.register(Image)
admin.site.register(PostImage)
admin.site.register(TagRating)
admin.site.register(Video)
admin.site.register(ExerciseType, ExerciseTypeAdmin)
admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(UserExercisePreference, UserExercisePreferenceAdmin)

from django.contrib import admin
from .models import Sound
from django.db.models import DateTimeField

class SoundAdmin(admin.ModelAdmin):
    using = 'mongodb'  # Set the database alias here
    list_display = ('name','file_path','uuid','tags','username','custom_file_name','user_timestamp')  # Update 'file_path' to 'audio_file'
    readonly_fields = ('uuid', 'user_timestamp')  # Update 'file_path' to 'audio_file'

     # Ensure the date hierarchy is based on created_at
    #date_hierarchy = 'created_at'

    # This makes sure the admin uses the appropriate widget for DateTimeField
    formfield_overrides = {
        DateTimeField: {'widget': admin.widgets.AdminSplitDateTime},
    }

    def get_queryset(self, request):
        # Tell Django to look for objects on the 'other' database.
        return super(SoundAdmin, self).get_queryset(request).using(self.using)

# Register the Sound model with the correct database alias
admin.site.register(Sound, SoundAdmin)




