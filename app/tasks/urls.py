from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TaskViewSet, UserRegistrationView

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/register/", UserRegistrationView.as_view(), name="register"),
]
