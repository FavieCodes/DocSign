from django.db import models
from django.contrib.auth.models import User
import uuid


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    name = models.CharField(max_length=255)
    original_file = models.FileField(upload_to='documents/originals/', blank=True, null=True)
    signed_file = models.FileField(upload_to='documents/signed/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'original_url': self.original_file.url if self.original_file else None,
            'signed_url': self.signed_file.url if self.signed_file else None,
            'created_at': self.created_at.strftime('%d %b %Y'),
            'updated_at': self.updated_at.strftime('%d %b %Y, %H:%M'),
        }
