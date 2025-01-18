from django.apps import AppConfig


class MusicAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'music_app'
#Same as init py - everything in the ready function will start on app startup.
    def ready(self):
        import music_app.signals