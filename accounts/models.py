from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        CREATOR = 'creator', 'Creator'
        VISITOR = 'visitor', 'Visitor'
        ADMIN   = 'admin',   'Admin'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.VISITOR,
    )
    bio = models.TextField(blank=True, default='')
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Helper properties — use these in views and permissions
    @property
    def is_creator(self):
        return self.role == self.Role.CREATOR

    @property
    def is_visitor(self):
        return self.role == self.Role.VISITOR

    @property
    def is_platform_admin(self):
        return self.role == self.Role.ADMIN

    def __str__(self):
        return f"{self.username} ({self.role})"