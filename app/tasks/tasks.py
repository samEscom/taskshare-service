import random
import time

from celery import shared_task
from django.contrib.auth.models import User

from .models import Task


@shared_task(bind=True, max_retries=5)
def send_email(self, user_id, task_id):
    """
    Mock function to simulate sending an email asynchronously.
    """
    try:
        # Simulate network delay for sending email
        time.sleep(2)

        # Randomly fail 80% of the time to test Celery retries
        if random.random() < 0.8:
            raise Exception("Random simulated network failure!")

        user = User.objects.get(id=user_id)
        task = Task.objects.get(id=task_id)

        # Simulate the email sending process
        print(f"[CELERY] Sending email to {user.email}...")
        print(f"[CELERY] Subject: Task Shared: {task.name}")
        print(f"[CELERY] Body: You have been granted access to the task '{task.name}'.")
        print(f"[CELERY] Email sent successfully to {user.email}")

        return True

    except Exception as exc:
        # If something fails (e.g., DB lookup fails, or simulated network error),
        # Celery will catch it and retry up to 5 times (as defined by max_retries).
        print(f"[CELERY] Error sending email: {exc}. Retrying...")

        # Exponential backoff retry (e.g., 5s, 25s, 125s...)
        self.retry(exc=exc, countdown=5**self.request.retries)
