import os
import uuid
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from mongoengine import connect, Document, StringField, UUIDField, ListField, DateTimeField
from django.http import HttpResponse, StreamingHttpResponse
from datetime import datetime
from django.conf import settings
import logging
logger = logging.getLogger(__name__)
timestamp_format = "%Y-%m-%d %H:%M:%S.%f%z"

# Define the Document for your MongoDB collection
class SoundFile(Document):
    original_name = StringField()
    file_path = StringField()
    tags = ListField(StringField())
    uuid = UUIDField(binary=False)
    username = StringField()
    custom_file_name = StringField()
    user_timestamp = DateTimeField()

def pretty_request(request):
    headers = ''
    for header, value in request.META.items():
        if not header.startswith('HTTP'):
            continue
        header = '-'.join([h.capitalize() for h in header[5:].lower().split('_')])
        headers += '{}: {}\n'.format(header, value)

    return (
        '{method} HTTP/1.1\n'
        'Content-Length: {content_length}\n'
        'Content-Type: {content_type}\n'
        '{headers}\n\n'
        '{body}'
    ).format(
        method=request.method,
        content_length=request.META['CONTENT_LENGTH'],
        content_type=request.META['CONTENT_TYPE'],
        headers=headers,
        body=request.body,
    )

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class MusicUploadView(APIView):
    parser_classes = [MultiPartParser]
    
    def handle_uploaded_file(self, uploaded_file, file_size):
        total_bytes_read = 0
        for chunk in uploaded_file.chunks():
            total_bytes_read += len(chunk)
            progress = total_bytes_read / file_size * 100
            yield f"data: {progress:.2f}\n\n"

            # Calculate progress and yield it as a percentage
            processed_bytes = total_bytes_read
            progress = (processed_bytes / file_size) * 100
            yield progress

            # Flush the response to send buffered data immediately
            yield "\n"  # Flush the response




    def post(self, request, format=None):
        print("request.files: ",request.FILES)
        #print("request.headers: ",request.headers)
        music_file = request.FILES.get('music')  # Access the uploaded file correctly
        if not music_file:
            return Response({'error': 'No music file found.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the tags from the request headers
        tags = request.data.getlist('tags[]', [])

        print("Received tags: ",tags)
        username = request.data.get('username', '')
        print("request.username: ",username)
        user_timestamp_str = request.data.get('timestamp', '')
        user_timestamp = datetime.strptime(user_timestamp_str, timestamp_format)
        print("Received timestamp: ",user_timestamp)
        custom_file_name = request.data.get('custom_file_name', '')
        print("Received custom_file_name: ",custom_file_name)
        
        
        # Calculate the total file size
        file_size = music_file.size

        # Handle the uploaded file and yield progress updates
        progress_generator = self.handle_uploaded_file(music_file, file_size)

        # Create a StreamingHttpResponse to send progress updates
        response = StreamingHttpResponse(progress_generator, content_type='text/event-stream')

        # Customize the destination path where you want to save the music file
        file_uuid = uuid.uuid4()
        file_name = f'{file_uuid}_{music_file.name}'
        file_path = os.path.join(settings.MEDIA_ROOT, 'audio_files', file_name)


        # Save the music file to the specified destination path
        with open(file_path, 'wb+') as destination:
            for chunk in music_file.chunks():
                destination.write(chunk)

        # Save the file information to MongoDB using mongoengine
        SoundFile(
            original_name=music_file.name,
            file_path=file_path,
            tags=tags,
            uuid=file_uuid,
            username=username,
            custom_file_name=custom_file_name,
            user_timestamp=user_timestamp,
        ).save()

        return response

def download_music(request, music_id):
    try:
        sound_file = SoundFile.objects.get(uuid=music_id)
        file_path = sound_file.file_path
        print(file_path)
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='audio/mpeg')
            response['Content-Disposition'] = f'attachment; filename={sound_file.original_name}'
            return response
    except SoundFile.DoesNotExist:
        return Response({'error': 'Music file not found.'}, status=status.HTTP_404_NOT_FOUND)

def delete_music(request, music_id):
    print('music_id', music_id)
    try:
        sound_file = SoundFile.objects.get(uuid=music_id)
        # Delete the associated file first
        if sound_file.file_path:
            try:
                os.remove(sound_file.file_path)
            except Exception as e:
                pass  # Handle the exception as needed
        sound_file.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except SoundFile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

def handle_options_for_delete(request, music_id):
    response = HttpResponse()
    response['Access-Control-Allow-Origin'] = '*'  # Allow all origins for simplicity
    response['Access-Control-Allow-Methods'] = 'DELETE, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type'
    return response
        
#_________________________________________________        
# Django API code

#from rest_framework.response import Response
#from rest_framework.views import APIView
#from rest_framework import status
#from mongoengine import Document, StringField, ListField
from django.http import JsonResponse


class AudioFilesForCategoryView(APIView):
    def get(self, request, category_name, format=None):
        try:
            if category_name == "All":
                audio_files = SoundFile.objects.all()
            else:
                audio_files = SoundFile.objects(tags__contains=category_name).all()
            
            audio_file_data = [
                {
                    'title': audio.original_name,
                    'ID': str(audio.uuid),  # Return UUID instead of filePath
                    'tags': audio.tags,
                    'username' : audio.username,
                    'userTimeStamp' : audio.user_timestamp,
                    'customFileName' : audio.custom_file_name
                }
                for audio in audio_files
            ]
            return JsonResponse(audio_file_data, safe=False)
        except Exception as e:
            return Response({'error': 'Failed to fetch audio files'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Filename: views.py in your 'music_app'
#view to load the feed / posts of the users
from rest_framework import pagination
from rest_framework.generics import ListAPIView
from music_app.models import Post
from music_app.serializers import PostSerializer

class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    page_query_param = 'page'

class PostListView(ListAPIView):
    serializer_class = PostSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        # select_related for "user" as it's a ForeignKey (one-to-many)
        # prefetch_related for "tags" as it's a ManyToManyField
        return Post.objects.select_related('user').prefetch_related('tags').all()
    



# views.py
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Audio, Image, Tag, PostTag, PostImage

class CreatePostWithAudioAndImageView(APIView):

    def post(self, request):
        logger.debug('request.data: %s', request.data)
        user = request.user
        description = request.data.get('description')
        audio_file = request.FILES.get('audio')
        image_file = request.FILES.get('image')
        tags = json.loads(request.data.get('tags', '[]'))

        duration = request.data.get('duration_in_milliseconds', None)

        if audio_file and image_file:
            audio = Audio.objects.create(
                user=user,
                audio_title=audio_file.name,
                audio_link=audio_file,
                duration_in_milliseconds=duration  # Set duration field
                # Add other fields as needed
            )

            image = Image.objects.create(
                user=user,
                image_file=image_file,
                # Add other fields as needed
            )

            post = Post.objects.create(
                user=user,
                description=description,
                audio=audio,
                # Remove the direct image ForeignKey field if it exists
                # Add other fields as needed
            )

            # Create a PostImage instance to link the image and post
            PostImage.objects.create(post=post, image=image)

            # Handle tags
            for tag_name in tags:
                tag, created = Tag.objects.get_or_create(tag_name=tag_name)
                PostTag.objects.create(post=post, tag=tag)

            return Response({'message': 'Post with audio and image created successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Both audio and image files are required'}, status=status.HTTP_400_BAD_REQUEST)
#Return the posts
from rest_framework.generics import ListAPIView
from .models import Post
from .serializers import PostSerializer

class ListPostsWithAudioAndImagesView(ListAPIView):
    queryset = Post.objects.all()  # Or filter as needed
    serializer_class = PostSerializer


# return ListPersonalGrowthCharacteristicsView for e.g. goal page
from rest_framework.generics import ListAPIView
from .models import PersonalGrowthCharacteristic
from .serializers import PersonalGrowthCharacteristicSerializer

class ListPersonalGrowthCharacteristicsView(ListAPIView):
    queryset = PersonalGrowthCharacteristic.objects.all()  # Adjust if you need any ordering or filtering
    serializer_class = PersonalGrowthCharacteristicSerializer


#get compositions by id
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Composition
from .serializers import CompositionSerializer

class CompositionDetailView(APIView):
    def get(self, request, composition_id):
        try:
            composition = Composition.objects.get(id=composition_id)
            serializer = CompositionSerializer(composition)
            return Response(serializer.data)
        except Composition.DoesNotExist:
            return Response({'error': 'Composition not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#Post a compositon post
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import (Audio, Composition, Post, Image, Tag, PostImage, 
                     CompositionAudio, CompositionTag)
from .serializers import (AudioSerializer, CompositionSerializer, ImageSerializer, 
                          PostSerializer, TagSerializer, CompositionAudioSerializer, 
                          CompositionTagSerializer)

import json

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Audio, Composition, Post, Image, Tag, PostImage
from .serializers import AudioSerializer, CompositionSerializer, ImageSerializer, PostSerializer

# Configure logger for the module (consider configuring in Django settings for entire project)
import logging
logger = logging.getLogger(__name__)

class PostContentView(APIView):
    def post(self, request, *args, **kwargs):
        # Log raw data and headers for debugging
        logger.debug(f"Raw data: {request.body}")
        logger.debug(f"Request headers: {request.headers}")
        logger.debug("Request.data: %s", request.data)  # Log the raw request data
        data = request.data

        # Initialize variables for content
        audio_instance = None
        composition_instance = None
        images = []
        uploaded_audio_files = {}  # To track uploaded audio files
        # Handle Audio
        if 'audio' in data:
            audio_serializer = AudioSerializer(data=data['audio'])
            if audio_serializer.is_valid():
                audio_instance = audio_serializer.save()
            else:
                return Response(audio_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Handle Composition - parsing the JSON string manually
        #composition_data = data.get('composition')
        #logger.debug("composition_data: %s",composition_data)
        logger.debug("request.data: %s",request.data)
        composition_data_str = data.get('composition')
        if composition_data_str:
            try:
                composition_data = json.loads(composition_data_str)

                # Create a serializer instance with parsed data
                composition_serializer = CompositionSerializer(
                    data=composition_data,
                    context={'request': request, 'uploaded_audio_files': uploaded_audio_files}
                )

                if composition_serializer.is_valid():
                    composition_instance = composition_serializer.save()
                else:
                    return Response(composition_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except json.JSONDecodeError:
                return Response({'error': 'Invalid JSON in composition field'}, status=status.HTTP_400_BAD_REQUEST)

        # Handle Images
        if 'images' in data:
            for image_data in data['images']:
                image_serializer = ImageSerializer(data=image_data)
                if image_serializer.is_valid():
                    image_instance = image_serializer.save(user=request.user)
                    images.append(image_instance)
                else:
                    return Response(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Create the Post instance using the created instances above
        post = Post.objects.create(
            user_id_backend_post=request.user,
            post_description=data.get('description'),
            audio_fk=audio_instance,
            composition_fk=composition_instance,
            # other fields...
        )

        # Associate images with the post
        for image in images:
            PostImage.objects.create(post=post, image=image)

        # Handle Tags - assuming post_data['tags'] is a list of tag names
        tags_list = data.get('tags', [])
        for tag_name in tags_list:
            tag, created = Tag.objects.get_or_create(tag_name=tag_name)

            # Get or create the PostTag object, avoiding duplicate entry
            post_tag, created = PostTag.objects.get_or_create(post=post, tag=tag)

        # Serialize the post to return
        post_serializer = PostSerializer(post)
        return Response({"message": "Post created successfully", "post": post_serializer.data}, status=status.HTTP_201_CREATED)
