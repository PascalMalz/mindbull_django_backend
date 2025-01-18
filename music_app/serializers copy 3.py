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
        fields = ['username']


    
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
    #Extract field composition_audios from post data and process them in CompositionAudioSerializer
    composition_audios = CompositionAudioSerializer(many=True)

    class Meta:
        model = Composition
        exclude = ('user_id_backend_composition',)

    def create(self, validated_data):
        
        composition_audios_data = validated_data.pop('composition_audios', [])
        user_id = validated_data.pop('user', None)
        # If user_id is not provided in the request, use the request user
        if not user_id:
            user_instance = self.context['request'].user  # Access user from request context
        else:
            user_instance = get_object_or_404(CustomUser, id=user_id)
        validated_data['user_id_backend_composition'] = user_instance
        parent_composition = Composition.objects.create(**validated_data)  # Define parent_composition here
        # Retrieve the user instance

        # Use a deque as a stack to handle composition audios iteratively
        stack = deque(composition_audios_data)
        logger.debug(f"Creating Parent Composition: {parent_composition.id}")
        logger.debug(f"Creating Parent Composition: {parent_composition.title}")
        while stack:
            ca_data = stack.pop()
            # Inside the while loop in the create method of CompositionSerializer
            user = ca_data.pop('user', None)  # Handle or store the user if needed

            content_type = ca_data.pop('content_type', None)  # Use pop to remove content_type
            content_data = ca_data.pop('content', None)

            if content_type == 'audio_file':
                # Handle audio creation
                logger.debug(f"Linking Audio to Parent Composition: {parent_composition.id}")
                logger.debug(f"Linking Audio to Parent Composition: {parent_composition.title}")
                audio_instance = self.create_audio_instance(content_data)
                CompositionAudio.objects.create(
                    composition=parent_composition,
                    content_type=content_type,
                    audio_file=audio_instance,
                    **ca_data  # Rest of the data, content_type is now removed
                )
            elif content_type == 'composition':
                # Handle nested composition
                nested_composition_serializer = CompositionSerializer(data=content_data, context=self.context)
                if nested_composition_serializer.is_valid(raise_exception=True):
                    nested_composition = nested_composition_serializer.save()
                    CompositionAudio.objects.create(
                        composition=nested_composition,
                        content_type=content_type,
                        **ca_data  # Rest of the data, content_type is now removed
                    )
                    # Add nested composition's audios to the stack
                    logger.debug(f"Creating Nested Composition linked to Parent: {parent_composition.id}")
                    logger.debug(f"Creating Nested Composition linked to Parent: {parent_composition.title}")
                    logger.debug(f"Nested Composition: {nested_composition.id}")
                    logger.debug(f"Nested Composition: {nested_composition.title}")        



        return parent_composition


    def create_audio_instance(self, audio_data):
        # Retrieve the user instance
        user_id = audio_data.pop('user', None)
        # If user_id is not provided in the request, use the request user
        if not user_id:
            user_instance = self.context['request'].user  # Access user from request context
        else:
            user_instance = get_object_or_404(CustomUser, id=user_id)
        
        # Separate tags data from other audio data
        tags_list = audio_data.pop('tags', [])  # This will be a list of tag identifiers (names, ids, etc.)

        # Get a list of valid field names for the Audio model
        valid_fields = {f.name for f in Audio._meta.get_fields()}

        # Filter the incoming audio_data to include only the fields that exist in the Audio model
        filtered_audio_data = {field: value for field, value in audio_data.items() if field in valid_fields}

        # Create the Audio instance without tags
        audio_instance = Audio.objects.create(user_id_backend_audio=user_instance, **filtered_audio_data)
        
        # Handle tags after the Audio instance is created
        # Find or create Tag instances for all tags in tags_list
        for tag_name in tags_list:
            tag, _ = Tag.objects.get_or_create(tag_name=tag_name)
            audio_instance.tags.add(tag)  # Using .add() method for many-to-many relationship

        return audio_instance



    
class PostSerializer(serializers.ModelSerializer):
    user_id_backend_post = PostUserSerializer(read_only=True)
    audio_fk = AudioSerializer(read_only=True)
    image_set = PostImageSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    composition_fk = CompositionSerializer(read_only=True)

    class Meta:
        model = Post
        fields = [
            'post_uuid', 'user_id_backend_post', 'post_description',
            'audio_fk', 'composition_fk', 'image_set', 'tags',
            'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        post = Post.objects.create(**validated_data)
        for tag_data in tags_data:
            tag, _ = Tag.objects.get_or_create(**tag_data)
            post.tags.add(tag)
        return post
# Add serializers for other models as needed
