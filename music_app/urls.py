# music_app/urls.py

from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings
#app_name = 'music_app'
urlpatterns = [
    path('download/<uuid:music_id>/', views.download_music, name='download_music'),
    path('api/upload_music/', views.MusicUploadView, name='upload-music'),
    path('audioFiles/<str:category_name>/', views.AudioFilesForCategoryView.as_view(), name='audio-files-category'),
    path('delete/<uuid:music_id>/', views.delete_music, name='delete_music'),
    path('delete/<uuid:music_id>/', views.handle_options_for_delete, name='delete_options'),
path('api/posts/', views.PostListView.as_view(), name='post-list'),
path('api/posts-audio-image/', views.ListPostsWithAudioAndImagesView.as_view(), name='list-posts'),
path('api/exercises/', views.ListExercisesByTypeView.as_view(), name='list-exercises'),
path('api/compositions/', views.ListCompositionPostView.as_view(), name='list-compositions'),

path('api/post-with-audio-image/', views.CreatePostWithAudioAndImageView.as_view(), name='upload_audio_image'),
path('api/personal_growth_characteristics/', views.ListPersonalGrowthCharacteristicsView.as_view(), name='personal_growth_characteristics'),
path('api/post_content/', views.PostContentView.as_view(), name='post_content'),
path('api/compositions/<uuid:composition_uuid>/', views.CompositionDetailView.as_view(), name='composition-detail'),
path('api/post-video/', views.CreatePostWithVideoView.as_view(), name='post-video'),
path('api/posts/<uuid:post_uuid>/like/', views.toggle_like_post, name='toggle-like-post'),
path('api/posts/<uuid:post_uuid>/check_like/', views.check_user_like_status, name='check-user-like-status'),
path('api/users/<uuid:user_id>/liked_posts/', views.get_liked_posts, name='liked-posts'),
path('api/posts/<uuid:post_uuid>/comment/', views.CreateCommentView.as_view(), name='create_comment'),
path('api/posts/<uuid:post_uuid>/comments/', views.CommentListView.as_view(), name='post-comments'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

