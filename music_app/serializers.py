# Filename: serializers.py in your 'music_app'
from rest_framework import serializers
from smart_user_management.models import CustomUser
from .models import Post, Audio, Image, Tag, PostImage

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['tag_name']

class AudioSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)


    class Meta:
        model = Audio
        fields = '__all__'  # Adjust fields as necessary

    def create(self, validated_data):
        # Filter audio data for Audio model fields
        user_id = validated_data.pop('user', None)
        tags_data = validated_data.pop('tags', [])
        audio = Audio.objects.create(**validated_data)
        for tag_data in tags_data:
            tag, _ = Tag.objects.get_or_create(**tag_data)
            AudioTag.objects.create(audio=audio, tag=tag)
        return audio


class ImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ['id', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image_file.url) if obj.image_file else None

class PostImageSerializer(serializers.ModelSerializer):
    image = ImageSerializer()

    class Meta:
        model = PostImage
        fields = ['image']

class PostUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username']

from smart_user_management.models import CustomUser

class PostUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'id', 'profile_picture']


    
# serializers.py
from rest_framework import serializers
from .models import PersonalGrowthCharacteristic
import logging
logger = logging.getLogger(__name__)

class PersonalGrowthCharacteristicSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalGrowthCharacteristic
        fields = ['category', 'name', 'description']  # or '__all__' if you prefer

#get composition:

from rest_framework import serializers
from .models import Composition, CompositionAudio, CompositionTag


class CompositionTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompositionTag
        fields = '__all__'

from rest_framework import serializers
from .models import CompositionAudio, Audio, Composition, AudioTag

class CompositionAudioSerializer(serializers.ModelSerializer):
    content = serializers.JSONField(write_only=True)  # Accept any JSON structure

    class Meta:
        model = CompositionAudio
        fields = '__all__'

    def create(self, validated_data):
        content_data = validated_data.pop('content', None)
        content_type = validated_data.get('content_type')
        if content_type == 'audio_file':
            # Deserialize the audio data and create an Audio instance
            audio_serializer = AudioSerializer(data=content_data)
            if audio_serializer.is_valid(raise_exception=True):
                audio = audio_serializer.save()
                validated_data['audio_file'] = audio
            return super().create(validated_data)
        # Note: Composition creation is handled by CompositionSerializer
        # If content_type is 'composition', just return without creating a composition here
        return super().create(validated_data)

import logging
logger = logging.getLogger(__name__)
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from collections import deque
#creating or updating nested objects through API (like creating a Composition along with its CompositionAudio instances in one request)
class CompositionSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super(CompositionSerializer, self).__init__(*args, **kwargs)


    #Extract field composition_audios from post data and process them in CompositionAudioSerializer
    composition_audios = CompositionAudioSerializer(many=True)

    class Meta:
        model = Composition
        exclude = ('user_id_backend_composition',)

    def create(self, validated_data):
        composition_audios_data = validated_data.pop('composition_audios', [])
        user_id = validated_data.pop('user', None)

        if not user_id:
            user_instance = self.context['request'].user
        else:
            user_instance = get_object_or_404(CustomUser, id=user_id)

        validated_data['user_id_backend_composition'] = user_instance
        parent_composition = Composition.objects.create(**validated_data)

        # Initialize a dictionary to store the serialized data
        json_db_representation = {
            "title": parent_composition.title,
            "compositionId":parent_composition.id,
            "composition_audios": self.serialize_composition_audios(composition_audios_data, parent_composition)
        }
        logger.debug(f'4json_db_representation: {json_db_representation}')  
            
        return parent_composition, json_db_representation

    def serialize_composition_audios(self, composition_audios_data, parent_composition):
        serialized_audios = []
        for ca_data in composition_audios_data:
            content_type = ca_data.pop('content_type', None)
            content_data = ca_data.pop('content', None)

            if content_type == 'audio_file':
                audio_instance = self.create_audio_instance(content_data)
                composition_audio = CompositionAudio.objects.create(
                    composition=parent_composition,
                    content_type=content_type,
                    audio_file=audio_instance,
                    **ca_data
                )
                serialized_audios.append({
                    "composition_audio_id": composition_audio.id,
                    "content_type": "audio_file",
                    "content": {"audioId": audio_instance.id}
                })
            elif content_type == 'composition':
                nested_composition_serializer = CompositionSerializer(data=content_data, context=self.context)
                if nested_composition_serializer.is_valid(raise_exception=True):
                    nested_composition, nested_serialized = nested_composition_serializer.save()
                    composition_audio = CompositionAudio.objects.create(
                    composition=nested_composition,
                    content_type=content_type,
                    **ca_data
                )
                    
                    serialized_audios.append({
                        "composition_audio_id": composition_audio.id,
                        "content_type": "composition",
                        "content": nested_serialized
                    })
        return serialized_audios


    
    def create_audio_instance(self, audio_data):
        processed_audio_titles = self.context['processed_audio_titles']
        audio_file_instances = self.context.get('audio_file_instances', {})
        request = self.context['request']
        logger.debug(f"1request in create_audio_instance: {request.user}")
        client_audio_path = audio_data.get('clientAppAudioFilePath')
        logger.debug(f"2client_audio_path: {client_audio_path}")  
        audio_title = audio_data.get('audio_title')
        # Handling existing audio instance
        if audio_title in processed_audio_titles:
            # Get the existing instance from the mapping
            return audio_file_instances[client_audio_path]
        # Retrieve or create user instance
        user_id = audio_data.pop('user', None)
        user_instance = request.user

        # Filter audio data for Audio model fields
        valid_fields = {f.name for f in Audio._meta.get_fields()}
        filtered_audio_data = {field: value for field, value in audio_data.items() if field in valid_fields}
        # Exclude 'tags' from filtered_audio_data if present
        filtered_audio_data.pop('tags', None)
        # Check for existing audio or create a new one
        audio_file = request.FILES.get(client_audio_path)  # Extract filename from path
        logger.debug(f"3audio_file: {audio_file}")
        logger.debug(f"4request.FILES: {request.FILES}")
        logger.debug(f"5audio_title: {audio_title}")
        
        logger.debug(f"6Processed audio titles: {processed_audio_titles}")

        if audio_file:

            audio_instance = Audio.objects.create(user_id_backend_audio=user_instance, audio_link=audio_file, **filtered_audio_data)
            logger.debug(f"10audio_instance: {audio_instance}")
            # Handle tags separately
            tags_list = audio_data.get('tags', [])
            tags = [Tag.objects.get_or_create(tag_name=tag_name)[0] for tag_name in tags_list]
            audio_instance.tags.set(tags)  # Use set() for many-to-many relationship

            processed_audio_titles.add(audio_title)
            logger.debug(f"11audio_file_instances: {audio_file_instances}")
            audio_file_instances[client_audio_path] = audio_instance
            return audio_instance
        else:
            # Handle the scenario where the file is not found in request.FILES
            raise serializers.ValidationError("Audio file not found in the request")



from rest_framework import serializers
from .models import Video

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['video_uuid', 'user', 'video_title', 'video_file']  # Adjust fields as needed


from rest_framework import serializers
from .models import Post
from .serializers import PostUserSerializer, AudioSerializer, PostImageSerializer, TagSerializer, VideoSerializer  # Import VideoSerializer

class PostSerializer(serializers.ModelSerializer):
    user_id_backend_post = PostUserSerializer(read_only=True)
    audio_fk = AudioSerializer(read_only=True)
    video_fk = VideoSerializer(read_only=True)  # Add video serializer
    image_set = PostImageSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    composition_fk = CompositionSerializer(read_only=True)

    class Meta:
        model = Post
        fields = [
            'post_uuid', 'user_id_backend_post', 'post_description','total_likes',
            'audio_fk', 'video_fk', 'composition_fk', 'image_set', 'tags',  # Include 'video_fk' in fields
            'created_at', 'updated_at',
        ]

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        post = Post.objects.create(**validated_data)
        for tag_data in tags_data:
            tag, _ = Tag.objects.get_or_create(**tag_data)
            post.tags.add(tag)
        return post
    
    def get_total_likes(self, obj):
        return obj.total_likes  # Calls the total_likes property on the Post model

# Add serializers for other models as needed

from rest_framework import serializers
from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    commentId = serializers.CharField(source='id', read_only=True)
    userId = serializers.CharField(source='user.id', read_only=True)
    userName = serializers.SerializerMethodField(read_only=True)  # Add this line

    class Meta:
        model = Comment
        fields = ['commentId', 'userId', 'post', 'description', 'created_at', 'updated_at', 'userName']  # Add 'userName' to fields
        read_only_fields = ['commentId', 'userId', 'created_at', 'updated_at']

    def get_userName(self, obj):
        return obj.user.username
    
    from rest_framework import serializers
from .models import Exercise

class ExerciseSerializer(serializers.ModelSerializer):
    tags = serializers.StringRelatedField(many=True)  # Adjust based on your Tag model
    exercise_type_name = serializers.CharField(
            source='exercise_type.display_name', read_only=True
        )  # Include `display_name` of ExerciseType
    class Meta:
        model = Exercise
        fields = [
            'exercise_uuid', 'name', 'description','instructions', 'thumbnail','media',
            'duration', 'xp', 'is_default', 'is_exclusive','exercise_type_name',
            'created_at', 'updated_at', 'tags', 'created_by'
        ]
