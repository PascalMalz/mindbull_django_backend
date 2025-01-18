from django.apps import AppConfig


class SmartUserManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'smart_user_management'
#Same as init py - everything in the ready function will start on app startup.
    def ready(self):
        import smart_user_management.signals