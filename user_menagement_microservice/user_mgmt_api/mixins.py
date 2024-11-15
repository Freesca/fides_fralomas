from django.utils import timezone

class UpdateLastActivityMixin():
    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        if request.user.is_authenticated:
            request.user.last_activity = timezone.now()
            request.user.save()
        return request