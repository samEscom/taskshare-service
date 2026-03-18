from django.utils import timezone
from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Task, TaskShare
from .serializers import TaskSerializer, UserSerializer, TaskShareSerializer

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only see my own active tasks
        return Task.objects.filter(created_by=self.request.user, is_active=True)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        # Update updated_by and updated_at on every modification
        serializer.save(updated_by=self.request.user, updated_at=timezone.now())

    def destroy(self, request, *args, **kwargs):
        # Logical delete
        instance = self.get_object()
        instance.is_active = False
        instance.updated_at = timezone.now()
        instance.updated_by = request.user
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        task = self.get_object()
        serializer = TaskShareSerializer(data=request.data)
        
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            try:
                shared_with = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(
                    {"error": "User does not exist"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Create or update share record
            share, created = TaskShare.objects.get_or_create(
                task=task,
                shared_with=shared_with
            )
            
            return Response(
                {"message": f"Task shared with {shared_with.username}"}, 
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
