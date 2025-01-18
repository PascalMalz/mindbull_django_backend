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
from rest_framework.generics import ListAPIView
from .models import Post  # Make sure to import your Post model
from .serializers import PostSerializer  # Import the serializer for Post
from rest_framework import pagination

class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    page_query_param = 'page'

class PostListView(ListAPIView):
    serializer_class = PostSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        """
        This method returns a queryset of Post objects, 
        ordered by the 'created_at' field in descending order.
        It includes select_related for optimizing "user" ForeignKey lookups,
        and prefetch_related for optimizing "tags" ManyToManyField lookups.
        """
        return Post.objects.select_related('user').prefetch_related('tags').order_by('created_at')
    



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
                user_id_backend_audio=user,
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
                user_id_backend_post=user,
                post_description=description,
                audio_fk=audio,
                # Remove the direct image ForeignKey field if it exists
                # Add other fields as needed
            )

            # Create a PostImage instance to link the image and post
            PostImage.objects.create(user_id_backend_post_image=user, image=image,post=post)

            # Handle tags
            for tag_name in tags:
                tag, created = Tag.objects.get_or_create(tag_name=tag_name)
                PostTag.objects.create(post=post, tag=tag)

            return Response({'message': 'Post with audio and image created successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Both audio and image files are required'}, status=status.HTTP_400_BAD_REQUEST)
#Return the posts



from rest_framework.generics import ListAPIView
from django.db.models import Q
from .models import Post, Tag  # Make sure to import Tag or any other necessary models
from .serializers import PostSerializer

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class ListPostsWithAudioAndImagesView(ListAPIView):
    
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        #logger.debug('request.data: %s', self.request)
        # Retrieve query params
        user_id = self.request.query_params.get('user_id_backend_post')
        logger.debug('user_id: %s', user_id)
        tags = self.request.query_params.get('tags')
        audio_fk = self.request.query_params.get('audio_fk')
        composition_fk = self.request.query_params.get('composition_fk')
        video_fk = self.request.query_params.get('video_fk')

        # Apply filters conditionally
        if user_id:
            queryset = queryset.filter(user_id_backend_post__id=user_id)
        
        if tags:
            tag_list = tags.split(',')
            queryset = queryset.filter(tags__name__in=tag_list).distinct()
        
        if audio_fk:
            queryset = queryset.filter(audio_fk__id=audio_fk)
        
        if composition_fk:
            queryset = queryset.filter(composition_fk__id=composition_fk)
        
        if video_fk:
            queryset = queryset.filter(video_fk__id=video_fk)

        return queryset





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
    def get(self, request, composition_uuid):
        try:
            logger.debug(f'get composition CompositionDetailView composition id: {composition_uuid}')
            composition = Composition.objects.get(composition_uuid=composition_uuid)
            mongo_composition_data = load_composition_from_mongo_db(composition_uuid)
            json_composition_result = replace_ids_with_data(mongo_composition_data)
            logger.debug(f'get composition CompositionDetailView: {json_composition_result}')
            return JsonResponse(json_composition_result)
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
# todo check if audio / composition id is already created (repost), then dont create the entry but reference on the db object. 
# Configure logger for the module (consider configuring in Django settings for entire project)
import logging
logger = logging.getLogger(__name__)
from pymongo import MongoClient
MONGO_URI = "mongodb://localhost:27017"  # Replace with your MongoDB URI
client = MongoClient(MONGO_URI)
db = client['sound_mongo']  # Replace with your MongoDB database name
mongo_collection = db['mongocompositions']  # Replace with your collection name
from bson import ObjectId

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class PostContentView(APIView):
    def post(self, request, *args, **kwargs):
        logger.debug(f"Raw data: {request.body}")
        logger.debug(f"Request headers: {request.headers}")
        logger.debug("Request.data: %s", request.data)  # Log the raw request data
        data = request.data
        # Initialize variables for content
        audio_instance = None
        composition_instance = None
        images = []
        audio_file_instances = {}  # To track uploaded audio files
        processed_audio_titles = set()
        json_db_representation = {}

        # Handle Composition - parsing the JSON string manually
        logger.debug("request.data: %s",request.data)
        composition_data_str = data.get('composition')
        if composition_data_str:
            try:
                composition_data = json.loads(composition_data_str)
                # Create a serializer instance with parsed data
                composition_serializer = CompositionSerializer(
                    data=composition_data,
                    context={'request': request, 'audio_file_instances': audio_file_instances, 'processed_audio_titles': processed_audio_titles, 'json_db_representation':json_db_representation}
                )

                if composition_serializer.is_valid():
                    composition_instance, json_db_representation = composition_serializer.save()
                else:
                    return Response(composition_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except json.JSONDecodeError:
                return Response({'error': 'Invalid JSON in composition field'}, status=status.HTTP_400_BAD_REQUEST)
        #logger.debug(json_db_representation)
        json_data = json.dumps(json_db_representation)
        logger.debug(json_data)
        # Create the Post instance using the created instances above
        post = Post.objects.create(
            user_id_backend_post=request.user,
            post_description=data.get('description'),
            audio_fk=audio_instance,
            composition_fk=composition_instance,
            # other fields...
        )

        # Handle Images
        image_file = request.FILES.get('image')
        if image_file:
            image = Image.objects.create(
                user=request.user,
                image_file=image_file,
            )
            PostImage.objects.create(post=post, image=image, user_id_backend_post_image=request.user)

        # Handle Tags - assuming post_data['tags'] is a list of tag names
        tags_list = data.get('tags', [])
        for tag_name in tags_list:
            tag, created = Tag.objects.get_or_create(tag_name=tag_name)

            # Get or create the PostTag object, avoiding duplicate entry
            post_tag, created = PostTag.objects.get_or_create(post=post, tag=tag)

        #MongoComposition.objects.create(json_db_representation)
        normalized_data = json.loads(json_data)
        logger.debug(f"Normalized Data to be inserted: {normalized_data}")

        try:
            result = mongo_collection.insert_one(normalized_data)
            mongo_db_id = str(result.inserted_id)
            #Store mongo db entry id on the highest (lvl) composition
            composition_instance.mongo_db_id = mongo_db_id
            composition_instance.save()
            logger.debug("Data inserted into MongoDB successfully")
        except Exception as e:
            logger.error(f"MongoDB insertion error: {e}")
            return Response({'error': 'Failed to insert data into MongoDB'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        

        # Serialize the post to return
        post_serializer = PostSerializer(post, context={'request': request})
        return Response({"message": "Post created successfully", "post": post_serializer.data}, status=status.HTTP_201_CREATED)


from django.http import JsonResponse
from pymongo import MongoClient
from bson import ObjectId
from .models import Post, Audio

from django.core.exceptions import ObjectDoesNotExist
from smart_user_management.models import CustomUser
from uuid import UUID

def replace_ids_with_data(data):
    if isinstance(data, list):
        # Process each item in the list
        return [replace_ids_with_data(item) for item in data]
    elif isinstance(data, dict):
        # Process each key-value pair in the dictionary
        new_data = {}
        for key, value in data.items():
            if key in ['composition_audio_id', 'audioId', 'compositionId']:
                try:
                    # Depending on the key, fetch the correct model instance and replace
                    if key == 'audioId':
                        instance = Audio.objects.get(id=value)
                    elif key == 'compositionId':
                        instance = Composition.objects.get(id=value)
                    else:  # 'composition_audio_id'
                        instance = CompositionAudio.objects.get(id=value)

                    # Merge the instance data into new_data
                    new_data.update(instance.to_dict())
                except ObjectDoesNotExist:
                    # Handle cases where the object does not exist
                    new_data[key] = None
            elif key == 'user' and isinstance(value, UUID):
                # Convert UUID to string for 'user' field
                new_data[key] = str(value)
            else:
                # Recursively process other keys
                new_data[key] = replace_ids_with_data(value)
        return new_data
    elif isinstance(data, ObjectId):
        # Convert ObjectId to string
        return str(data)
    else:
        # Return the data as is for other types
        return data


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class ListCompositionPostView(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def list(self, request, *args, **kwargs):
        response = super(ListCompositionPostView, self).list(request, *args, **kwargs)
        posts_data = response.data

        # MongoDB setup
        MONGO_URI = "mongodb://localhost:27017"
        client = MongoClient(MONGO_URI)
        db = client['sound_mongo'] 
        mongo_collection = db['mongocompositions']  

        for post in posts_data:
            
            composition = post.get('composition_fk')  # Adjust field name as necessary
            composition_id = composition.get('id')
            if composition_id:
                logger.debug(f'composition_id: {composition_id}')
                composition = Composition.objects.get(id=composition_id)
                mongo_db_id = composition.mongo_db_id
                if mongo_db_id:
                    logger.debug(f'mongo_db_id: {mongo_db_id}')
                    mongo_data = mongo_collection.find_one({'_id': ObjectId(str(mongo_db_id))})
                    logger.debug(f'mongo_data: {mongo_data}')
                    if mongo_data:
                        processed_data = replace_ids_with_data(mongo_data)
                        logger.debug(f'processed_data {processed_data}')
                        post['composition_data'] = processed_data

        # Convert posts_data to JSON string and log it
        json_posts_data = json.dumps(posts_data, default=str) #default=str importent to convert e.g. uuid
        logger.debug(f"JSON formatted posts data: {json_posts_data}")
        return JsonResponse(posts_data, safe=False)


def load_composition_from_mongo_db(composition_uuid):
    composition = Composition.objects.get(composition_uuid=composition_uuid)
    mongo_db_id = composition.mongo_db_id
    # MongoDB setup
    MONGO_URI = "mongodb://localhost:27017"
    client = MongoClient(MONGO_URI)
    db = client['sound_mongo']

    mongo_collection = db['mongocompositions']  
    mongo_composition_data = mongo_collection.find_one({'_id': ObjectId(str(mongo_db_id))})
    logger.debug(f'mongo_data: {mongo_composition_data}')
    if mongo_composition_data:
        return mongo_composition_data


# views.py
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Audio, Image, Tag, PostTag, PostImage, Video

class CreatePostWithVideoView(APIView):

    def post(self, request):
        logger.debug('request.data: %s', request.data)

        user = request.user
        description = request.data.get('description')
        video_file = request.FILES.get('video')
        tags = json.loads(request.data.get('tags', '[]'))

        if video_file:
            video = Video.objects.create(
                user=user,
                video_title=video_file.name,
                video_file=video_file,
                # Add other fields as needed
            )

            post = Post.objects.create(
                user_id_backend_post=user,
                post_description=description,
                video_fk=video,
                # Link the video to the post
                # Add other fields as needed
            )

            # Handle tags
            for tag_name in tags:
                tag, created = Tag.objects.get_or_create(tag_name=tag_name)
                PostTag.objects.create(post=post, tag=tag)

            return Response({'message': 'Post with video created successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Video file is required'}, status=status.HTTP_400_BAD_REQUEST)

#Endpoint to like / unlike a post
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Post

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_like_post(request, post_uuid):
    logger.debug('toggle_like_post with post_uuid: %s', post_uuid)
    post = get_object_or_404(Post, post_uuid=post_uuid)
    user = request.user

    if user in post.likers.all():
        post.likers.remove(user)
        liked = False
    else:
        post.likers.add(user)
        liked = True

    return JsonResponse({'liked': liked, 'total_likes': post.likers.count()})

# Endpoint to check if user already liked a post:
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Post

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_user_like_status(request, post_uuid):
    logger.debug('check_user_like_status with post_uuid: %s', post_uuid)
    post = get_object_or_404(Post, post_uuid=post_uuid)
    is_liked_by_user = post.likers.filter(id=request.user.id).exists()

    return JsonResponse({'is_liked_by_user': is_liked_by_user})


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import CustomUser, Post
from .serializers import PostSerializer

@api_view(['GET'])  # Changed to GET to better reflect the operation
@permission_classes([IsAuthenticated])
def get_liked_posts(request, user_id):
    """
    Retrieve all posts liked by a specific user and serialize them using the PostSerializer.
    
    Args:
    user_id (UUID): UUID of the user whose liked posts are to be retrieved.
    
    Returns:
    Response: Contains a serialized list of liked posts.
    """
    # Ensure the user exists
    user = get_object_or_404(CustomUser, pk=user_id)
    
    # Retrieve all posts liked by the user
    liked_posts = Post.objects.filter(likers=user).prefetch_related('likers', 'audio_fk', 'video_fk', 'image_set', 'tags')
    
    # Serialize data using PostSerializer
    serializer = PostSerializer(liked_posts, many=True, context={'request': request})
    
    return Response(serializer.data)





from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Post, Comment
from .serializers import CommentSerializer


class CreateCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        post_uuid = kwargs.get('post_uuid')
        post = get_object_or_404(Post, post_uuid=post_uuid)

        # Correct way to use uuid module to convert string to UUID object
        # However, since we need to pass the Post object, this step is unnecessary
        # post_uuid_obj = uuid.UUID(post_uuid)

        # Copy request.data to a mutable structure
        data = request.data.copy()
        # Assign the Post object's ID as the value for the 'post' field
        # Note: The serializer expects an ID (primary key), not a UUID object
        data['post'] = post.id

        # Now, pass the modified data to the serializer
        serializer = CommentSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=201)
        else:
            logger.debug('Serializer errors: %s', serializer.errors)
            return Response(serializer.errors, status=400)



        

# views.py
from rest_framework.generics import ListAPIView
from django.shortcuts import get_object_or_404
from .models import Comment, Post
from .serializers import CommentSerializer
import logging

logger = logging.getLogger(__name__)

class CommentListView(ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        """
        This view returns a list of all comments for the post as determined by the post_uuid portion of the URL.
        """
        post_uuid = self.kwargs.get('post_uuid')
        logger.debug('Fetching comments for post UUID: %s', post_uuid)

        # Ensure you are using post__post_uuid to filter based on the UUID field of the Post model.
        post = get_object_or_404(Post, post_uuid=post_uuid)
        return Comment.objects.filter(post=post).order_by('-created_at')


from rest_framework.generics import ListAPIView
from django.db.models import Q
from .models import Exercise, UserExercisePreference
from .serializers import ExerciseSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny

class ListExercisesByTypeView(ListAPIView):

    #Here specificly allowed api!
    #todo check authentication
    authentication_classes = []  # Disable authentication for this view
    permission_classes = [AllowAny]  # Allow any user (authenticated or not) to access
    """
    API view to retrieve exercises filtered by type and user preferences, ordered by duration in ascending order.
    """
    #authentication_classes = [JWTAuthentication]
    #permission_classes = [IsAuthenticated]
    serializer_class = ExerciseSerializer

    def get_queryset(self):
        exercise_type = self.request.query_params.get('exercise_type')

        queryset = Exercise.objects.filter(
            is_active=True,
            exercise_type__name=exercise_type
        )

        if self.request.user.is_authenticated:
            user_preferences = UserExercisePreference.objects.filter(
                user=self.request.user
            ).values_list('exercise_id', flat=True)

            queryset = queryset.filter(Q(is_default=True) | Q(id__in=user_preferences))
        else:
            queryset = queryset.filter(is_default=True)

        queryset = queryset.order_by('duration')

        # Debug: Print serialized data
        serializer = self.get_serializer(queryset, many=True)
        logger.debug(serializer.data)

        return queryset