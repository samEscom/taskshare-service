from rest_framework import viewsets
from .models import Task
from .serializers import TaskSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def perform_create(self, serializer):
        # Automatically set created_by/updated_by to the current user
        # For this demo, we can set them to the request user
        # (Assuming authentication is set up, otherwise we might need a dummy)
        serializer.save(created_by=self.request.user, updated_by=self.request.user)
