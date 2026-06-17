from django.db import models
from django.contrib.auth.models import User


class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='verification')
    code = models.CharField(max_length=6)
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.code} ({'Confirmed' if self.is_confirmed else 'Pending'})"
